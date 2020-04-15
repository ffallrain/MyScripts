#!/usr/bin/python
import sys,os
import fpdb
import numpy as np

infile = sys.argv[1]

# load all coords
all_coords = list()
all_frame = list()
for frame in fpdb.next_frame(infile):
    tmp_coords = list()
    for line in frame:
        if len(line) > 6 and line[12:16].strip()=='CA':
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            tmp_coords.append((x,y,z))
    all_coords.append(tmp_coords)
    all_frame.append(frame)


# make matrix
def rmsd(a,b):
    n = len(a)
    s = 0.
    for i in range(n):
        s += (a[i][0]-b[i][0])**2+(a[i][1]-b[i][1])**2+(a[i][2]-b[i][2])**2
    r = (s/n)**0.5
    return r

N = len(all_coords)
matrix = np.ndarray( shape = (N,N) )
for i in range(N):
    for j in range(N):
        matrix[i][j] = rmsd(all_coords[i],all_coords[j])

with open("matrix.dat",'w') as ofp:
    for i in range(N):
        for j in range(N):
            ofp.write( "%8.5f "%matrix[i][j])
        ofp.write("\n") 


# run nmrclust
with open("nmrclust.in",'w') as ofp:
    ofp.write("N\n")
    ofp.write("matrix.dat\n")
    ofp.write("\n")

result = os.popen("nmrclust < nmrclust.in").readlines()

# analyse
def next_cluster(lines):
    tmp = list()
    for line in lines:
        if "Cluster Number" in line:
            print line,
            c_n = int(line.split()[-1])
        if "Cluster Spread" in line:
            print line,
            c_s = float(line.split()[-1])
        if "Representative Model" in line:
            print line,
            c_r = int(line.split()[-1]) - 1 
        if "Members" in line:
            print line,
            m = [ int(x)-1  for x in line.split()[1:] ]
            yield c_n,c_s,c_r,m
            print ""

        
with open("all_representive.pdb",'w') as arofp:
    for cluster in next_cluster(result):
        c_n,c_s,c_r,m = cluster
        with open("cluster_%d.pdb"%c_n,'w') as cofp:
            for i in m :
                cofp.write("MODEL    %d\n"%i)
                for line in all_frame[i]:
                    if "END" not in line:
                        cofp.write(line)
                cofp.write("ENDMDL\n")
        arofp.write("MODEL    %d\n"%i)
        for line in all_frame[c_r]:
            if "END" not in line:
                arofp.write(line)
        arofp.write("ENDMDL\n")
            
    
