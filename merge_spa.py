#!/usr/bin/python
import fpdb
import sys,os

dir1 = 'part1'
dir2 = 'part2'

dirs = sys.argv[1:-1]
outfile = sys.argv[-1]

graphics = list()
for DIR in dirs:
    graphics.append('%s/%s'%(DIR,'graphic.pdb'))

pdbs = list()
for graphic in graphics:
    pdbs.append(fpdb.fPDB(graphic))

waters = list()
for pdb in pdbs:
    waters.append(pdb.topology.get_water_residues())

all_waters = list()
for tmp in waters:
    all_waters.extend(tmp)

cutoff = 1.0
nr_waters = list()
for test_water in all_waters:
    dist = 9999
    neighbor_water = None
    for water in nr_waters:
        tmp_dist = fpdb.dist_2(test_water.atoms[0],water.atoms[0])
        if tmp_dist > dist:
            pass
        else:
            dist = tmp_dist
            neighbor_water = water
    if dist>=cutoff:
        nr_waters.append(test_water)
    else:
        if  test_water.atoms[0].bf > neighbor_water.atoms[0].bf :
            nr_waters.remove(neighbor_water)
            nr_waters.append(test_water)
        else:
            pass

with open(outfile,'w') as ofp:
    for resi in pdbs[0].topology.get_protein_residues():
        resi.write_pdb(ofp)
    for water in nr_waters:
        water.write_pdb(ofp)
    
