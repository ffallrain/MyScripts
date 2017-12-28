#!/usr/bin/python
import sys,os

infile = sys.argv[1]
outfile = 'out.pdb'

ofp = open(outfile,'w')
for line in open(infile):
    if len(line)>=6 and line[:6] in ("ATOM  ","HETATM"):
        x = float(line[30:38])
        newx = 0 - x 
        newline = "%s%8.3f%s"%(line[:30],newx,line[38:])
    else:
        newline = line
    ofp.write(newline)

