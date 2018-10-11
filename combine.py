#!/usr/bin/python
import sys,os
import fpdb

ligfile = sys.argv[1]
flexfile = sys.argv[2]
recfile = sys.argv[3]
outfile = sys.argv[4]

# load residues
flex_resi = dict()
for resi in fpdb.fPDB(flexfile).topology.residues:
    flex_resi[resi.index] = resi

rec_resi = fpdb.fPDB(recfile).topology.residues

lig_resi = fpdb.fPDB(ligfile).topology.residues[0]

# forge flex resides, add "N", "HN", "C", "O" 
for template_resi in rec_resi:
    index = template_resi.index
    if flex_resi.has_key(index):
        target_resi = flex_resi[index]
        for atom in template_resi.atoms:
            if target_resi.atoms_d.has_key(atom.name):
                atom.posi = target_resi.atoms_d[atom.name].posi

# output residues
ofp = open(outfile,'w')
for resi in rec_resi:
    resi.write_pdb(ofp)
ofp.write("TER\n")
lig_resi.write_pdb(ofp)
ofp.write("END\n")
ofp.close()
