#!/usr/bin/python
import sys,os

distance = lambda a,b: ( (a[0]-b[0])**2 +(a[1]-b[1])**2 +(a[2]-b[2])**2 )**0.5
n=0
output=list()
for line in open(sys.argv[1],"r"):
    if line[0:6] not in ("HETATM","ATOM  "):
        continue
    index=int(line[6:11])
    x=float(line[30:38])
    y=float(line[38:46])
    z=float(line[46:54])
    an=line[12:16]
    if "OW" in an or ("O" in an and "HW" not in an):
        n+=1
        output.append("%6d  O     %9.6f   %9.6f   %9.6f   247%6d%6d\n"%( index,   x,       y,      z,        index+1,index+2))
        o=(x,y,z)
    if "H1" in an or "HW1" in an:
        output.append("%6d  H     %9.6f   %9.6f   %9.6f   248%6d\n"%( index,   x,       y,      z,        index-1))
        h1=(x,y,z)
    if "H2" in an or "HW2" in an:
        output.append("%6d  H     %9.6f   %9.6f   %9.6f   248%6d\n"%( index,   x,       y,      z,        index-2))
        h2=(x,y,z)
        if distance(o,h1)>2 or distance(o,h2)>2:
            print distance(o,h2)
            n-=1
            output=output[:-3]
        
output=["%d\n"%(n*3),]+output

ofp=open(sys.argv[2],"w")
for line in output:
    ofp.write(line)
ofp.close()

