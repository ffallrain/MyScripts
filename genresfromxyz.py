#!/usr/bin/python
import sys,os
infile,outfile=sys.argv[1:3]

ofp=open(outfile,"a")
force = 2.5
n = 0 
for line in open(infile,"r"):
    if n <= 1 :
        n += 1
        continue
    n += 1
    items=line.split()
    if len(items) < 5: continue
    index=int(items[0])
    atomtype=items[1]
    atomclass=int(items[5])
    if "H" not in atomtype and atomclass != 247:
        ofp.write("restrain-position %d %f\n"%(index,force))
ofp.close()
    

