#!/usr/bin/python
import sys,os

infile1 = sys.argv[1]
infile2 = sys.argv[2]


coord1 = dict()
coord2 = dict()
for line in open(infile1):
    if len(line)>=6 and line[:6] in ("HETATM",'ATOM  '):
        if line[21] == 'A':
            name = line[12:22]
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coord1[name] = x,y,z
    
for line in open(infile2):
    if len(line)>=6 and line[:6] in ("HETATM",'ATOM  '):
        if line[21] == 'A':
            name = line[12:22]
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coord2[name] = x,y,z


s = 0.
n = 0
for key in coord1.keys():
    x1,y1,z1 = coord1[key]
    x2,y2,z2 = coord2[key]
    s += (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2
    n += 1

rmsd = (s/n)**0.5

print rmsd
