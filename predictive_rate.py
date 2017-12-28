#!/usr/bin/python
import sys,os
import numpy as np

reffile,reqfile=sys.argv[1:3]

def distance(a,b):
    return ( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 ) ** 0.5

ref=list()
for line in open(reffile,"r"):
    if line[0:6] not in ["HETATM","ATOM  "]:
        continue
    resi=line[17:20]
    if resi not in ["SOL","WAT","HOH"] :
        continue
    atom=line[12:16].strip()
    if atom not in ["O","OW"]:
        continue
    x=float(line[30:38])
    y=float(line[38:46])
    z=float(line[46:54])
    ref.append((x,y,z))
N_ref=len(ref)

req=list()
for line in open(reqfile,"r"):
    if line[0:6] not in ["HETATM","ATOM  "]:
        continue
    resi=line[17:20]
    if resi not in ["SOL","WAT","HOH"] :
        continue
    atom=line[12:16].strip()
    if atom not in ["O","OW"]:
        continue
    x=float(line[30:38])
    y=float(line[38:46])
    z=float(line[46:54])
    occ = float(line[60:66])
    req.append((x,y,z,occ))

print "Total_crystal_waters: %d"%N_ref

print "DIST_CUTOFF|OCC_CUTOFF",
for occ_cutoff in np.arange(11)*0.1:
    print occ_cutoff,
print 

for cutoff in np.arange(16)*0.1:
    print cutoff ,
    for occ_cutoff in np.arange(11)*0.1:
        N_req = 0
        N_match=0
        for a in req:
            if a[3] < occ_cutoff :
                continue
            else:
                N_req += 1
                for b in ref:
                    dist=distance(a,b)
                    if dist<cutoff:
                        N_match+=1
        print "%d"%N_match,
    print 

N_reqs = list()
for occ_cutoff in np.arange(11)*0.1:
    N_req = 0
    N_match=0
    for a in req:
        if a[3] < occ_cutoff :
            continue
        else:
            N_req += 1
    N_reqs.append(N_req)

print "Total_predicted_water:",
for N_req in N_reqs :
    print N_req,
print

print "Predictive_rate:"
for cutoff in np.arange(16)*0.1:
    print cutoff ,
    for occ_cutoff,N_req in zip(np.arange(11)*0.1,N_reqs):
        N_match=0
        for a in req:
            if a[3] < occ_cutoff :
                continue
            else:
                for b in ref:
                    dist=distance(a,b)
                    if dist<cutoff:
                        N_match+=1
        try:
            print "%f"%(N_match*1.0/N_ref),
        except:
            print "%f"%0.0,
    print 

print "True_positive_rate:"
for cutoff in np.arange(16)*0.1:
    print cutoff ,
    for occ_cutoff,N_req in zip(np.arange(11)*0.1,N_reqs):
        N_match=0
        for a in req:
            if a[3] < occ_cutoff :
                continue
            else:
                for b in ref:
                    dist=distance(a,b)
                    if dist<cutoff:
                        N_match+=1
        try:
            print "%f"%(N_match*1.0/N_req),
        except:
            print "%f"%0.0,
    print 
