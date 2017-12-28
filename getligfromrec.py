#!/usr/bin/python
import sys,os

content=open(sys.argv[1],"r").read()
resis=content.strip().split(":")
pocketresis=list()
for i in range(len(resis)):
    index,chain,resi=resis[i].split("_")
    index=int(index)
    pocketresis.append("%s %s %3d"%(resi,chain,index))

for line in open(sys.argv[2],"r"):
    for item in pocketresis:
        if item in line:
            print line,
            break
