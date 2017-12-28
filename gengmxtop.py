#!/usr/bin/python
import sys,os
usage='''
Generate gromacs top file , firstly use tleap to get amber paramters, then translate to gmxtop by amb2gmx.pl
Usage $0 rec.pdb ssbond.list outputname
# e.g. outputname=rec, then output will be rec.gro and rec.top
'''
if len(sys.argv)<4:
    print usage
    sys.exit()
infile,ssfile,outname=sys.argv[1:4]

sslist=list()
for line in open(ssfile,"r"):
    a,b=line.split()
    sslist.append((a,b))

ofp=open("gengmxtop_leap.in","w")
head='''
source leaprc.ff99SB
rec = loadpdb %s
'''%infile
tail='''
savepdb rec gengmxtop_tmp.pdb
saveamberparm rec prmtop inpcrd
quit
'''
ofp.write(head)
for (i,j) in sslist:
    ofp.write("bond rec.%s.SG rec.%s.SG\n"%(i,j))
    ofp.write("remove rec.%s rec.%s.HG\n"%(i,i))
    ofp.write("remove rec.%s rec.%s.HG\n"%(j,j))
ofp.write(tail)
ofp.close()
os.system("tleap -f gengmxtop_leap.in")

os.system("amb2gmx.pl --prmtop prmtop --crd inpcrd --outname %s"%outname)
