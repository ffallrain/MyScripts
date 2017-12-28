#!/usr/bin/python
import sys,os

pdbfile = 'minimize.pdb'
xyzfile = 'minimize.xyz'
bakfile = 'bak.minimize.xyz'
tmpfile = 'tmp_blablabla.xyz'

os.system("cp %s %s"%(xyzfile,bakfile) )

# read a-axis, b- c- ..
a = b = c = 0
for line in open(pdbfile):
    if 'CRYST1' in line:
        a = float(line.split()[1])
        b = float(line.split()[2])
        c = float(line.split()[3])
        break

# read and write xyz
ofp = open(tmpfile,'w')
ifp = open(xyzfile)
n = 0
for line in ifp:
    n += 1
    if n == 2 :
        items = line.split()
        if items[0] != '1':
            print "Already has pbc line, STOP"
            ifp.close()
            ofp.close()
            os.system('rm %s'%tmpfile)
            sys.exit()
        else:
            abcline = ("%12.6f"*6+"\n")%(a,b,c,90,90,90)
            ofp.write(abcline)
    ofp.write(line)
ifp.close()
ofp.close()
os.system("mv %s %s"%(tmpfile,xyzfile) )
print "Done."
        
