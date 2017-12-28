#!/usr/bin/python
import pp
import math
import sys,os
import random
import time

__doc__="A script to perform replica exchange dynamics by Tinker.dynamic.x ---- write by Qiuyu fu\n"

###############################################
###            INPUT PARAMETERS             ###
###############################################

REPLICA    = ['f%d'%x for x in range(24)]
NODES      = tuple( [ "k%d.hn.org"%x for x in (116,117,118,119,120,121,122) ] ) # NODE:the chief node should NOT be in this list
TIME       = 20000        # ps
Ts         = [ 230.00, 236.04, 242.20, 248.48, 254.88, 261.39, 268.04, 274.81, 281.71, 288.76, 295.92, 303.23, 310.68, 318.27, 326.01, 333.89, 341.94, 350.13, 358.48, 367.00, 375.69, 384.54, 393.57, 402.77 ]
NP         = 4            # n core cpu for each dynamic
NSTEP      = 500   
STEP_LENGTH= 2            # fs
TIME_DUMP  = 0.50         # ps
CANONICAL  = "NPT"
T_CONST    = 298.0        # K
P_CONST    = 1.0          # atm
PREFIX     = "freezing"
KEYFILE    = "tinker.key"
PARAMFILE  = "amoebapro13_water2014.prm"
PROG       = '/opt/tinker633/dynamic.x'
ENERGYLOG  = 'REMD_freezing_energy.log'
RELOG      = 'REMD_freezing_exchange.log'
USR        = os.popen("whoami").read().strip()
PATH       = os.popen("pwd"   ).read().strip()

############################################
##   constant values are defined here     ##
############################################

kB         = 1.380622e-23                 # J/K
r_kB       = 1/kB
kB_kcal    = kB/4.184/1000.0*6.022169e23  # kcal/K/mol
r_kB_kcal  = 1/kB_kcal


##########################################################
##   Two functions to calculate accept possibility      ##
##########################################################
def P_nvt(T1, T2, E1, E2):
    P = r_kB_kcal*(1./T1-1./T2)*(E1-E2)
    if P>0.0: return 1.0 
    P = math.exp(P)
    P = min(1, P)
    return P
def P_npt(T1, T2, E1, E2, P1, P2, V1, V2):
    P = r_kB_kcal*(1./T1-1./T2)*(E1-E2) + r_kB*(P1/T1-P2/T2)*1e5*(V1-V2)*1e-30
    if P>0.0: return 1.0
    P = math.exp(P)
    P = min(1, P)
    return P

###############################################
##   a function to grep Volume, Potential    ##
##   return (energy,volume,avg_energy,a,b,c) ##
###############################################
def get_mdinfo(logfile):
    aver_e = 0 
    energy = None
    for line in open(logfile,"r"):
        if   line.find('Current Potential')>-1:
            energy = float(line.split()[2])
        elif line.find('Potential Energy' )>-1:
            aver_e = float(line.split()[2])
        elif line.find('Lattice Lengths'  )>-1:
            line   = line.split()
            x      = float(line[2])
            y      = float(line[3])
            z      = float(line[4])
            volume = x*y*z
    return (energy, volume, aver_e, x, y, z)


##################################################################
##   a function to run tinker simulation, return run status     ##
##################################################################

def dynamic( prog=None,logfile="dynamic.log",param="param",directory=None,debug=False):
    if debug: return 
    os.chdir(directory)
    tmp=os.popen("%s < %s >> %s"%(prog,param,logfile)).read()
#    print "%s < %s >> %s"%(prog,param,logfile)
    os.chdir("..")
    return 


#############################################################
###    Run multi-dynamics for each replica for 1 N_step   ###
#############################################################

def multi_dynamics(replica=REPLICA,Ts=Ts,jobserver=None,steps=NSTEP,step_length=STEP_LENGTH,time_dump=TIME_DUMP,canonical=CANONICAL,T=T_CONST,P=P_CONST):

    ##### Assertion and preparation
    assert jobserver!=None
    jobserver.submit(func=dynamic,args=(None,None,None,None,True))()

    ##### Run dynamics on each node, answer[] collects the run state
    answers=list()
    for i in range(len(replica)):  
        ##### make param file
        name    = replica[i]
        dir     = "%s_%s"     %(PREFIX,name)
        xyz     = "%s_%s.xyz" %(PREFIX,name)
        logfile = "%s.log"    %name
        param   = "%s.param"  %name
        t       = Ts[i]
        os.chdir( dir )
        assert os.path.isfile("tinker.key") 
        ofp=open(param,"w")
        ofp.write("%s\n"%xyz)
        ofp.write("%s\n"%steps)
        ofp.write("%s\n"%step_length)
        ofp.write("%s\n"%time_dump)
        if canonical=="NVE":
            ofp.write("%s\n"%"1")
        elif canonical=="NVT": 
            ofp.write("%s\n"%"2")
            ofp.write("%s\n"%t)
        elif canonical=="NPT":
            ofp.write("%s\n"%"4")
            ofp.write("%s\n"%t)
            ofp.write("%s\n\n\n"%P)
        ofp.close()
        os.chdir("..") 
        ##### Submit job on ppserver
        _    = jobserver.submit(func=dynamic, args=( PROG,logfile,param,dir ),depfuncs=(),modules=('os',))
        ##### Save job handle
        answers.append(_)

    ##### Extract MD result
    result=list()
    for i in range(len(replica)):  
        answers[i]()
        t       = Ts[i]
        name  = replica[i]
        os.chdir("%s_%s"%(PREFIX,name))  
        energy,volume,aver_e,x,y,z=get_mdinfo(logfile="%s.log"%name)
        result.append( (name,t,energy,volume,aver_e) )
        os.chdir("..") 
    return result
        
#####################################################################
###    Do exchange, take the result of multi_dynamics as input,   ###
###           Return a exchanged list replica                     ###
#####################################################################
def exchange(result,ensemble="NVT",eoflag=0):
    if ensemble == "NVT" :
        N=len(result)
        replica=[ x[0] for x in result ]
        for i in range(N):
            if i%2==eoflag%2 and i+1<N:
                t1=result[i][1]
                e1=result[i][2]
                t2=result[i+1][1]
                e2=result[i+1][2]
                p=P_nvt(t1,t2,e1,e2)
                if random.random()<p:
                    replica[i],replica[i+1]=replica[i+1],replica[i]
#                    print "Debug:exchanged t1:%f t2:%f e1:%f e2:%f p:%f"%(t1,t2,e1,e2,p)
    return tuple(replica)


###############################################################
####     Set up directories and files                      ####
###############################################################

def setup_file(prefix=PREFIX,replica=REPLICA):
    assert os.path.isfile(KEYFILE)
    assert os.path.isfile(PARAMFILE)
    assert os.path.isfile(PROG)
    if not os.path.isdir("BACKUP"):
        os.mkdir("BACKUP")
    for i in replica:
        if os.path.isfile("%s.log"%i):
            os.system("mv %s.log BACKUP"%(i))
        if os.path.isfile("%s.param"%i):
            os.system("mv %s.param BACKUP"%(i))
#        assert os.path.isfile("%s_%s.xyz"%(PREFIX,i))
        if not os.path.isdir("%s_%s"%(PREFIX,i)):
            os.mkdir("%s_%s"%(PREFIX,i))
        os.system("mv %s.param %s.log %s_%s.xyz %s_%s"%(i,i,PREFIX,i,PREFIX,i))
        os.system("cp %s %s_%s"%(KEYFILE,PREFIX,i))

def setup_pp(nodes=NODES):
    assert len(REPLICA)==len(Ts)
    nton=8/NP
    print "Tasks on one node:%d"%nton
    usr=USR
    path=PATH
    for node in nodes:
        os.system("ssh %s@%s 'killall ppserver.py'"%(usr,node))
        os.system("ssh %s@%s 'cd %s;ppserver.py -w %d' &"%(usr,node,path,nton))
    server=pp.Server(ppservers=nodes)
    server.set_ncpus(nton)
    os.system("sleep 10")
    print "Active nodes:"
    print server.get_active_nodes()
    return server

def setup_random():
    random.seed(time.time())

def setup(prefix=PREFIX,replica=REPLICA,nodes=NODES):
    setup_file()
    server=setup_pp()
    setup_random()
    return server

###############################################################
######       destroy  parallel environment                #####
###############################################################

def destroy(server=None,nodes=NODES):
    for node in nodes:
        os.system("ssh qyfu02@%s 'killall ppserver.py'"%node)
    server.destroy()
        

###############################################################
####   The Main Function                                   ####
###############################################################

server=setup()
replica=REPLICA

Eofp=open(ENERGYLOG,"w")
Rofp=open(RELOG,"w")
for t in range( int((TIME*1000)/(NSTEP*STEP_LENGTH)) ):
    tt=t*NSTEP*STEP_LENGTH*0.001 # ps 
    result=multi_dynamics(replica=replica,jobserver=server)
    for i in result:
        Eofp.write("%8.3f "%tt)
        Eofp.write("%s "%i[0])
        Eofp.write("%f "%i[1])
        Eofp.write("%f "%i[2])
        Eofp.write("%f "%i[3])
        Eofp.write("%f "%i[4])
        Eofp.write("\n")
    replica=exchange(result,eoflag=t)
    Rofp.write("%f "%tt)
    Rofp.write(" ".join(replica))
    Rofp.write("\n")
    server.print_stats()
    print ">>>>> remd_tinker.py:  Time: %f exchanged %d times"%(tt,t+1)
    sys.stdout.flush()
    Eofp.flush()
    Rofp.flush()

destroy(server=server)
