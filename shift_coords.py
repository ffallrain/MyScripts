#!/usr/bin/python
import sys,os
import fpdb

infile = sys.argv[1]
outfile = sys.argv[2]
shift_x = float(sys.argv[3])
shift_y = float(sys.argv[4])
shift_z = float(sys.argv[5])

ofp = open(outfile,'w')
for line in open(infile):
    if len(line)>=6 and line[:6] in ("ATOM  ","HETATM"):
        x = float(line[30:38]) - shift_x
        y = float(line[38:46]) - shift_y
        z = float(line[46:54]) - shift_z
        ofp.write( "%s%8.3f%8.3f%8.3f%s"%(line[:30],x,y,z,line[54:]) )
    else:
        ofp.write(line)
