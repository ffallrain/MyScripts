#!/usr/bin/python
import sys,os

element_index = dict()

for line in open(sys.argv[1]):
    if "ATOM" not in line and "HETATM" not in line:
        print line,
    else:
        name = line[12:16].strip()
        element = name[0]
        if not element_index.has_key(element):
            element_index[element] = 0
            newname = element+"%d"%element_index[element]
        else:
            element_index[element] += 1
            newname = element+"%d"%element_index[element]
        newline = "%s %-3s%s"%(line[:12],newname,line[16:])
        print newline,
            
            
