#!/usr/bin/python
import sys,os
import numpy as np

def next_pose(infile):
    n = 0 
    pose = dict()
    for line in open(infile):
        if "MODEL" in line:
            n = int(line.split()[1])
            pose = dict()
        elif "ENDMDL" in line:
            yield n,pose
        elif "ATOM" in line:
            name = line[12:16].strip()
            if 'H' not in name:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                pose[name] = (x,y,z)
            else:
                pass
        else:
            pass

def distance_2(a,b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 

def rmsd(pose1,pose2):
    keys = pose1.keys()
    n = len(keys)
    s = 0.0
    for key in keys:
        coord1 = pose1[key]
        coord2 = pose2[key]
        s += distance_2(coord1,coord2)
    return (s/n)**0.5
        
if len(sys.argv) > 1:
    infile = sys.argv[1]

    ## read pose
    poses = list()
    indexes = list()
    for index, pose in next_pose(infile):
        poses.append(pose)
        indexes.append(index)

    nframe = len(poses)

    ## make matrix 
    matrix = np.ndarray( shape = (nframe,nframe) )
    for i in range(nframe):
        for j in range(nframe):
            matrix[i][j] = rmsd(poses[i],poses[j])

    ## output 
    for i in range(nframe):
        for j in range(nframe):
            print "%8.5f "%matrix[i][j],
        print ""
else :
    print "Usage $0 input.pdb"
    
