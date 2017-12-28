#!/usr/bin/python
import sys,os
import fpdb

infile = sys.argv[1]
N = int(sys.argv[2])


count = 0
for frame in fpdb.next_frame(infile):
    if count % N == 0 :
        try:
            os.mkdir("spa_%d"%(count/N))
        except:
            pass
        ofp = open("spa_%d/traj.pdb"%(count/N),'w')
        print ">>>>> Traj splited %d"%(count/N)
    
    for line in frame:
        ofp.write(line)
    
    print "----- Frame %d"%count
    count += 1
