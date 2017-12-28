#!/usr/bin/python
import sys,os
usage="""
Add 'TER' to each end of peptide
Usage $0 in.pdb out.pdb
"""
if len(sys.argv)<3:
    print usage
    sys.exit()
infile,outfile=sys.argv[1:3]

sys.stderr.write("!!!!! Warning addter.py is not completed by now, make sure 'N' atom is the first of each residue\n")

Nxyz,Cxyz=(None,None)
Newresiflag=True
oldindex=0
oldline=""

def distance(A,B):
    if None in (A,B):
        return 0
    dist=( (A[0]-B[0])**2 + (A[1]-B[1])**2 + (A[2]-B[2])**2 ) ** 0.5 
    return dist 

ofp=open(outfile,"w")
for line in open(infile,"r"):
    if line[0:6] not in ("ATOM  " , "HETATM"):
        ofp.write(line)
        continue
    if line[12:16].strip()=="N":
        Nxyz=(float(line[30:38]),float(line[38:46]),float(line[46:54]))
    if line[12:16].strip()=="C":
        Cxyz=(float(line[30:38]),float(line[38:46]),float(line[46:54]))
    index=int(line[22:26])
    if index!=oldindex and distance(Nxyz,Cxyz)>2.0:
        ofp.write("TER\n")
    oldindex=index
    ofp.write(line)
ofp.close()
