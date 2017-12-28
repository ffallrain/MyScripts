#!/usr/bin/python
import sys,os

infile = sys.argv[1]
outfile = "transformed.%s"%infile

ofp = open(outfile,'w')
for line in open(infile):
    # line = line.replace("ITEM: ENTRIES index c_2[1] c_2[2] c_2[3] c_2[4]","ITEM: ATOMS id type xs ys zs")
    if "TEM: ENTRIES index" in line:
        line = "ITEM: ATOMS id type xs ys zs\n"
    line = line.replace("NUMBER OF ENTRIES","NUMBER OF ATOMS")
    ofp.write(line)
ofp.close()

    
