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

minx = miny = minz = 9999
for line in open(infile):
    if len(line)>=6 and line[:6] in ("HETATM","ATOM  "):
        x = float(line[30:38])
        y = float(line[38:46])
        z = float(line[46:54])

        minx = min(x,minx)
        miny = min(y,miny)
        minz = min(z,minz)

with open(outfile,'w') as ofp:
    for line in open(infile):
        if len(line)>=6 and line[:6] in ("HETATM","ATOM  "):
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            nx = x-minx
            ny = y-miny
            nz = z-minz
            ofp.write("%s%8.3f%8.3f%8.3f%s"%(line[:30],nx,ny,nz,line[54:]))
        else:
            ofp.write(line)
        
