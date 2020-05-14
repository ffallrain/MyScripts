#!/usr/bin/env python
import sys,os

os.system("cat rec.pdb lig.pdb |grep -v END > tmp.pdb")
os.system("mm.py rec_solv_ions.1.pdb tmp.pdb")
os.system("grep -E 'ATOM|HETATM' lig.pdb |cut -b 17-20|uniq > tmpname")
os.system("grep -f tmpname tmp.pdb > lig_shift.pdb")

sys.exit()

if False:
    # origin rec xyz
    oxyz = None
    for line in open("rec.pdb"):
        if len(line)>=6 and line[:6] == 'ATOM  ':
            if line[12:16].strip() == 'CA':
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                oxyz = (x,y,z)
                break

    # minim rec xyz
    mxyz = None
    for line in open("rec_solv_ions.1.pdb"):
        if len(line)>=6 and line[:6] == 'ATOM  ':
            if line[12:16].strip() == 'CA':
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                mxyz = (x,y,z)
                break

    # write lig_shift.pdb
    with open("lig_shift.pdb",'w') as ofp:
        for line in open("lig.pdb"):
            if len(line)>=6 and line[:6] in ('ATOM  ',"HETATM"):
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                nx = x + (mxyz[0]-oxyz[0])
                ny = y + (mxyz[1]-oxyz[1])
                nz = z + (mxyz[2]-oxyz[2])
                print(x,nx)
                ofp.write("%s%8.3f%8.3f%8.3f%s"%(line[:30],nx,ny,nz,line[54:]))
            else:
                ofp.write(line)
    print(oxyz)
    print(mxyz)
