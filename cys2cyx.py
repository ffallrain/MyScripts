#!/usr/bin/python
import sys,os
usage="""
Modify CYS to CYX if S-S bond exist
Usage $0 in.pdb out.pdb ssbond-map
"""
if len(sys.argv)<4:
    print usage
    sys.exit()
infile,outfile,ssfile=sys.argv[1:4]

def distance(A,B):
    if None in (A,B): return 0
    dist=( (A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2 ) ** 0.5 
    return dist 

sgs=dict()
for line in open(infile,"r"):
    if line[0:6] not in ("ATOM  ","HETATM"): continue
    if line[12:16].strip()=="SG" and line[17:20]=="CYS":
        index=int(line[22:26])
        x,y,z=float(line[30:38]),float(line[38:46]),float(line[46:54])
        sgs[index]=(x,y,z)

ssbonds=list()
keys=sgs.keys()
pairs=[(i,j) for i in keys for j in keys if i<j]
ofp=open(ssfile,"w")
for (i,j) in pairs:
    dist=distance(sgs[i],sgs[j])
    if dist<2.5:
        ofp.write("%d %d\n"%(i,j))
        ssbonds.append(i)
        ssbonds.append(j)
ofp.close()

ofp=open(outfile,"w")        
for line in open(infile,"r"):
    if len(line)>20 and line[17:20]=="CYS":
        index=int(line[22:26])
        if index in ssbonds:
            line="%sCYX%s"%(line[0:17],line[20:])
    ofp.write(line)
ofp.close()
