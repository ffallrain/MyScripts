#!/usr/bin/python
import sys,os

if len(sys.argv)<3:
    print "usage: $0 in.top in.itp"
topfile=sys.argv[1]
posrefile=sys.argv[2]

os.system("mv %s bak_%s"%(topfile,topfile))

ofp=open(topfile,"w")
flag=False
for line in open("bak_%s"%topfile):
    if line.find("moleculetype")!= -1 :
        if flag:
            ofp.write("#ifdef POSRES\n")
            ofp.write('#include "posre.itp"\n')
            ofp.write("#endif\n")
        else:
            flag=True
    ofp.write(line)
ofp.close()     
