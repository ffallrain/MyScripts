#!/usr/bin/python
import sys,os
import fpdb

infile = sys.argv[1]
outfile = sys.argv[2]

print ">>>>> Centering traj.."
n = 0
center_coord = None
pdb = fpdb.fPDB(infile)
center_coord = pdb.find_protein_center()
print "----- Center Coordination :",center_coord

n = 0
ofp = open(outfile,'w')
pdb = fpdb.fPDB(infile)
pdb.center(center_coord)
pdb.write_pdb(ofp)

print "----- All done."
