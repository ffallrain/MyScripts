#!/usr/bin/python
import sys,os
import fpdb

if len(sys.argv)<=2:
    print "Usage $0 in.pdb out.pdb"
    sys.exit()
else:
    infile = sys.argv[1]
    outfile = sys.argv[2]

x = y = z = 9999

pdb = fpdb.fPDB(infile)
for residue in pdb.topology.residues:
    for atom in residue.atoms:
        x = min(x,atom.posi[0])
        y = min(y,atom.posi[1])
        z = min(z,atom.posi[2])

print 'x: %f'%x
print 'y: %f'%y
print 'z: %f'%z

for residue in pdb.topology.residues:
    for atom in residue.atoms:
        atom.posi[0] = atom.posi[0] - x
        atom.posi[1] = atom.posi[1] - y
        atom.posi[2] = atom.posi[2] - z
    
pdb.write_pdb(outfile)
        
