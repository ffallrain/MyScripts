#!/usr/bin/python
import sys,os

if len(sys.argv)<3:
	print "$0 inpdb outpdb"
	sys.exit()
inpdb=sys.argv[1]
outpdb=sys.argv[2]

ofp=open(outpdb,"w")
ifp=open(inpdb,"r")
while True :
	line=ifp.readline()
	if not line : break 
	if line.find("1HW")== -1 :
		ofp.write(line.replace("2HW"," HW"))
	else:
		nextline=ifp.readline()
		ofp.write(nextline)
		ofp.write(line.replace("1HW"," HW"))
		continue
ifp.close()
ofp.close()

