#!/usr/bin/python
import sys,os
usage='''
sort residue from 1, help to set up MD system.
$0 in.pdb out.pdb
'''
if len(sys.argv)<3:
    print usage
    sys.exit()
else:
    infile,outfile=sys.argv[1:3]

ofp=open(outfile,"w")
ifp=open(infile,"r")

formerindex=0
currentindex=0
index=0
for line in ifp:
    if line[0:4]!="ATOM":
        newline=line
    else:
        currentindex=int(line[22:26])
        if currentindex!=formerindex:
            index=index+1
        formerindex=currentindex
        newline="%s%4d%s"%(line[:22],index,line[26:])
    ofp.write(newline)
ofp.close

print "Total %d residues"%index
