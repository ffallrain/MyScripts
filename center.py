#!/usr/bin/python
import sys,os

infile = sys.argv[1]
tmpgro = 'TMP.gro'
tmppdb = 'TMP.pdb'
gmx    = 'gmx'

# get box size
if infile[-3:] == 'gro':
    last = None
    for line in open(infile):
        last = line
    print last
    x,y,z = last.split()
    x = float(x)
    y = float(y)
    z = float(z)
    tmp = tmpgro
elif infile[-3:] == 'pdb':
    cryst1 = None
    for line in open(infile):
        if 'CRYST1' in line :
            cryst1 = line
    print cryst1
    x = float(cryst1.split()[1])/10.
    y = float(cryst1.split()[2])/10.
    z = float(cryst1.split()[3])/10.
    tmp = tmppdb
    

os.system("cp %s %s"%(infile,tmp))
os.system("%s editconf -f %s -o %s -center %f %f %f "%(gmx,tmp,infile,x/2.,y/2.,z/2.) )
os.system("rm %s"%tmp)
print "Done"
    
