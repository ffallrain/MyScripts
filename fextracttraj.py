#!/usr/bin/python
import sys,os

prmtop=sys.argv[1]
anchor=sys.argv[2]
infile=sys.argv[3]
outfile=sys.argv[4]
tmpfile='tmptmptmp.file.pdb'

trajin='''
parm %s
trajin %s 0 100000000 1
autoimage anchor %s
trajout %s
go
'''%(prmtop,infile,anchor,tmpfile)

ofp=open("traj.in","w")
ofp.write(trajin)
ofp.close()

os.system("cpptraj< traj.in")
os.system("rm traj.in")

ofp=open(outfile,"w")
for line in open(tmpfile,"r"):
    if "TER" in line:
        continue
    at=line[12:16].strip()
    if len(at) == 4 and at[-1]=="H":
        at="H"+at[:3]
        line="%s%s%s"%(line[:12],at,line[16:])
    if line[0:6] in ('END   ',"CRYST1"):
        continue
    line=line.replace("O   WAT","OW  SOL")
    line=line.replace("H1  WAT","HW1 SOL")
    line=line.replace("H2  WAT","HW2 SOL")
    ofp.write(line)
ofp.close()

os.system("rm %s"%tmpfile)

