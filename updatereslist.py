#!/usr/bin/python
import sys,os

usage='''
Usage:$0 tmplig.pdb rec.pdb lig.pdb res.list
'''
tmplig,rec,lig,reslist=sys.argv[1:5]

ofp=open("tmpligcoord","w")
for line in open(tmplig,"r"):
    x,y,z=float(line[30:38]),float(line[38:46]),float(line[46:54])
    ofp.write("%7.2f0%7.2f0%7.2f0\n"%(x,y,z))
ofp.close()

os.system("grep -f tmpligcoord %s > %s"%(rec,lig))

res=list()
ofp=open(reslist,"w")
for line in open(lig,"r"):
    if line[0:6] not in ["HETATM","ATOM  "]:continue
    name,index=line[17:20],line[22:26]
    if (name,index) not in res:
        res.append((name,index))
        ofp.write("%s %s\n"%(name,index))
ofp.close()

