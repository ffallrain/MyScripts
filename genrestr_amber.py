#!/usr/bin/python 
import sys,os

print "Group Restraint"
print "1000.0"
for line in open(sys.argv[1],'r'):
    if line[0:6] not in ["HETATM","ATOM  "]:
        continue
    else:
        atomindex=int(line[6:11])
        atomname=line[12:16]
        residue=line[17:20]
        if residue in ["WAT","SOL","HOH"]:
            continue
        elif "H" in atomname :
            continue
        else:
            print "ATOM %d %d"%(atomindex,atomindex)
        
print "END"
print "END"
