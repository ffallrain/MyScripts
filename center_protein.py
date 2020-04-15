#!/usr/bin/python
import sys,os
import fpdb
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', help='input pdb file')
parser.add_argument('-o',default='out.pdb',help='output pdb file')
parser.add_argument('-center', nargs=3, help='Center', type=float ,default = (0,0,0) )
parser.add_argument('-box', nargs=3, help='Box size', type=float ,default = (0,0,0) )
args = parser.parse_args()

infile = args.i
outfile = args.o
box = args.box
center = args.center

print ">>>>> Centering traj.."
n = 0
center_coord = None
pdb = fpdb.fPDB(infile)
if center == (0,0,0):
    center_coord = pdb.find_protein_center()
else:
    center_coord = center
print "----- Center Coordination :",center_coord

n = 0
ofp = open(outfile,'w')
pdb = fpdb.fPDB(infile)
pdb.center(center_posi = center_coord,box = box)
pdb.write_pdb(ofp)

print "----- All done."
