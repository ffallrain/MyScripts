#!/usr/bin/python
import sys,os
from math import acos

## usage
usage = '''
$0 inpdb > out.dat
'''
if len(sys.argv)<=1:
    print usage
    sys.exit()
else:
    infile=sys.argv[1]

############################################################
#######       Parameters are defined here            #######
############################################################

parameters=None

######################################################
######  a function to calculate hydrogen bond  #######
######################################################

def distance_2(a,b):
    return  (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 

lower_cutoff=2.04-0.4
upper_cutoff=2.04+0.4
lower_cutoff_2=lower_cutoff**2
upper_cutoff_2=upper_cutoff**2
lower_angle_cutoff_cos = -1.
upper_angle_cutoff_cos = -0.5
def is_hbond( o1,h,o2 ):
    if abs(h[0]-o2[0])>upper_cutoff:
        return False
    if abs(h[1]-o2[1])>upper_cutoff:
        return False
    if abs(h[2]-o2[2])>upper_cutoff:
        return False
    d_oo_2=distance_2(o1,o2)
    d_o1_h_2=distance_2(o1,h)
    d_o2_h_2=distance_2(o2,h)
    if d_o2_h_2 > upper_cutoff_2 or d_o2_h_2 < lower_cutoff_2 :  ### 
        return False
    cosangle=(d_o1_h_2+d_o2_h_2-d_oo_2)/((4*d_o1_h_2*d_o2_h_2)**0.5)
    if not  lower_angle_cutoff_cos<cosangle<upper_angle_cutoff_cos:
        return False
    return True

def next_frame(ifp):
    model = list()
    n = 0
    for line in ifp:
        if "MODEL" in line:
            model = list()
            n = int(line.split()[1])
        elif "ENDMDL" in line:
            yield n,model
        else:
            model.append(line)

def calc_hbond(n_frame,frame):
    ##################################################
    #######       Load coordinates            ########
    ##################################################

    waters=list()
    hcoords=list()
    heavycoords=list()

    ######--------------*.xyz file--------------######
    for line in frame:
        if line[0:6] not in ('HETATM',"ATOM  "):
            continue
        x=float(line[30:38])
        y=float(line[38:46])
        z=float(line[46:54])
        index=int(line[6:11])
        name=line[12:16]
        res = line[17:20]
        if "H" in name and res in ('HOH','SOL','WAT') :
            hcoords.append((x,y,z,index))
        elif  "O" in name and res in ('HOH','SOL','WAT'):
            heavycoords.append((x,y,z,index))

    # assert len(heavycoords)*2 == len(hcoords)
    for i in range(len(heavycoords)):
        waters.append( (heavycoords[i],hcoords[2*i],hcoords[2*i+1]) )

    ###################################################
    ######  screen hydrogen bonds                ######
    ###################################################
    hbonds=list()
    for water in waters:
        o=water[0]
        h1=water[1]
        h2=water[2]
        for o2 in heavycoords:
            if is_hbond(o,h1,o2):
                # hbonds.append( (o[3],h1[3],o2[3]))
                hbonds.append( (o,h1,o2))
            if is_hbond(o,h2,o2):
                # hbonds.append( (o[3],h2[3],o2[3]))
                hbonds.append( (o,h2,o2))

    ##################################################
    #####           Output                       #####
    ##################################################
#    print len(hbonds)
    for hbond in hbonds :
        # print n_frame,hbond[0],hbond[1],hbond[2]
        # print n_frame,hbond[0],hbond[2]
        print n_frame,hbond[0][0],hbond[0][1],hbond[0][2],hbond[2][0],hbond[2][1],hbond[2][2]

#### Main
if True:
    ifp = open(infile)
    for n_frame,frame in next_frame(ifp):
        calc_hbond(n_frame,frame)
