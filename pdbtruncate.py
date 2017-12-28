#!/usr/bin/python
import sys,os
usage='''
Truncate protein structure into a binding site
$0 protein.pdb lig.pdb output.pdb truncatesize
'''
if len(sys.argv)<5:
    print usage
    sys.exit()
else:
    proteinfile,ligandfile,outputfile,truncatesize=sys.argv[1:5]
    truncatesize=float(truncatesize)

##### load in ligand coordinates
ligcoords=list()
for line in open(ligandfile,"r"):
    if line[:6] not in ("ATOM  ","HETATM"):
        continue
    else:
        x,y,z=float(line[30:38]),float(line[38:46]),float(line[46:54])
        ligcoords.append((x,y,z))

##### Load in receptor coordinates
residues=dict()
indexes=list()
for line in open(proteinfile,"r"):
    if line[:6] not in ("ATOM  ","HETATM"):continue
    resiindex=int(line[22:26])
    x,y,z=float(line[30:38]),float(line[38:46]),float(line[46:54])
    if residues.has_key(resiindex):
        residues[resiindex].append((x,y,z))
    else:
        residues[resiindex]=[(x,y,z)]
        indexes.append(resiindex)

##### Calculate distances
distance=list()
def dist_cal(A,B):
    mindist=9999
    for (x1,y1,z1) in A:
        for (x2,y2,z2) in B:
            dist=( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 )**0.5
            if mindist>dist:
                mindist=dist
    return mindist
for index in indexes:
    dist=dist_cal(residues[index],ligcoords)
    distance.append(dist)

##### Truncate
#print "Distance:"
#for i in distance:
#    print "%8.3f"%i
saveindexes=list()
for i in range(len(distance)):
    if distance[i]<truncatesize:
        saveindexes.append(i)

enlargesel=saveindexes[:]
for j in saveindexes:
    enlargesel.append(j+1)
    enlargesel.append(j+2)
enlargesel.sort()
lite=list()
for i in enlargesel:
    if i not in lite:
        lite.append(i)
enlargesel=lite[:]

saveindexes=enlargesel[:]
for j in saveindexes:
    if j+2 in saveindexes:
        enlargesel.append(j+1)
    if j+3 in saveindexes:
        enlargesel.append(j+1)
        enlargesel.append(j+2)
    if j+4 in saveindexes:
        enlargesel.append(j+1)
        enlargesel.append(j+2)
        enlargesel.append(j+3)
enlargesel.sort()
lite=list()
for i in enlargesel:
    if i not in lite:
        lite.append(i)
#print lite

##### Output
ofp=open(outputfile,"w")
ifp=open(proteinfile,"r")
for line in ifp:
    if line[:6]!="ATOM  ":
        newline=line
    else:
        index=int(line[22:26])
        if index in lite:
            newline=line
        else:
            newline=""
    ofp.write(newline)
ifp.close()
ofp.close()
