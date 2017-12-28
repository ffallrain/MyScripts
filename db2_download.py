#!/usr/bin/python
import sys,os
import zinc_db2

for line in open(sys.argv[1]):
    number = int(line[4:])
    print ">>>>>> ",number
    try:
        zinc_db2.down_db2(number)
    except:
        print "###### Fail"
    else:
        print ">>>>>> Done"
