#!/usr/bin/python
import sys,os
import fpdb

infile = sys.argv[1]
outfile = sys.argv[2]
center_frame = int(sys.argv[3])


print ">>>>> Centering traj.."
n = 0
center_coord = None
for model in fpdb.next_frame(infile):
    n += 1
    if n == center_frame:
        pdb = fpdb.fPDB(model)
        print "A"
        center_coord = pdb.find_protein_center()
        
        break
print "----- Center Coordination :",center_coord

n = 0
ofp = open(outfile,'w')
for model in fpdb.next_frame(infile):
    n += 1
    pdb = fpdb.fPDB(model)
    pdb.center(center_coord)
    pdb.write_pdb(ofp)
    print "----- Model %d Done"%n

print "----- All done."
