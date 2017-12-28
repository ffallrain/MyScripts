#!/usr/bin/env python
import sys,os
import fpdb

after = 'shift_in_box.pdb'
init = 'tleap_out.pdb'
lig = 'lig.pdb'

pdb1 = fpdb.fPDB(init)
pdb2 = fpdb.fPDB(after)

coord1 = pdb1.topology.residues[0].atoms[0].posi
coord2 = pdb2.topology.residues[0].atoms[0].posi
print coord1
print coord2

dx = coord2[0] - coord1[0]
dy = coord2[1] - coord1[1]
dz = coord2[2] - coord1[2]

with open('lig_shift.pdb','w') as ofp:
    for line in open(lig):
        if len(line) >= 6 and line[:6] in ("ATOM  ","HETATM"):
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            nx = x  + dx
            ny = y  + dy
            nz = z  + dz
            newline = "%s%8.3f%8.3f%8.3f%s"%(line[:30],nx,ny,nz,line[54:])
        else:
            newline = line
        ofp.write(newline)

