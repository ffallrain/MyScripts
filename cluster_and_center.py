#!/usr/bin/python
import sys,os
import numpy as np
from sklearn.cluster import MiniBatchKMeans

infile = sys.argv[1]

def next_frame(infile):
    lines = list()
    flag = False
    for line in open(infile):
        if "MODEL" in line:
            flag = True
            lines.append(line)
        elif "ENDMDL" in line:
            flag = False
            lines.append(line)
            yield lines
            lines = list()
        if flag:
            lines.append(line)
            
frames = list()
for frame in next_frame(infile):
    frames.append(frame)

coords = list()
for frame in frames:
    tmpcoord = list()
    for line in frame:
        if "ATOM" in line:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            tmpcoord.append( x )
            tmpcoord.append( y )
            tmpcoord.append( z )
    coords.append(tmpcoord)
            
N_CLUSTER = 3
npcoords = np.array( coords )

if True:  # minibatch kmeans. (very fast batch kmeans)
        mbk = MiniBatchKMeans(init='k-means++', n_clusters=N_CLUSTER, batch_size=1,
                              n_init=10, max_no_improvement=10, verbose=0,
                              random_state=0)

        mbk.fit(npcoords)
        mbk_means_labels_unique = np.unique(mbk.labels_)
        clu_group = mbk.labels_
        clu_centers = mbk.cluster_centers_

clusters = set(clu_group)
ofps = list()
for cluster in clusters:
    ofp = open("clustered_%d.pdb"%cluster,'w')
    ofps.append(ofp)

for i in range(len(frames)):
    cluster = clu_group[i]
    for line in frames[i]:
        ofps[cluster].write(line)
for ofp in ofps:
    ofp.close()

### centroid structure
for j in range(len(clu_centers)):
    center =  clu_centers[j]
    frame0 = frames[0]
    with  open('center_%d.pdb'%j,'w') as ofp:
        i = 0
        for line in frame0:
            if "ATOM" in line:
                x,y,z = center[i:i+3]
                # z = z+18000
                newline = "%s%8.3f%8.3f%8.1f%s"%(line[:30],x,y,z,line[54:])
                i += 3
            else:
                newline = line
            ofp.write(newline)


