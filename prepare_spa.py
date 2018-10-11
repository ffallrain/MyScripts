#!/usr/bin/python
import fpdb
import sys,os

traj = 'prod/traj.pdb' 

os.system("shift_lig.py")

frame = next( fpdb.next_frame(traj) )

with open("prod/a1.pdb",'w') as ofp:
    for line in frame:
        ofp.write(line)

with open("prod/rec.pdb",'w') as ofp:
    for resi in fpdb.fPDB(frame).topology.get_protein_residues():
        resi.write_pdb(ofp)

n = 0
with open("runspa.bash",'w') as ofp:
    ofp.write("#!/bin/bash\n")
    ofp.write("source ~/.bashrc\n")
    while True:
        if os.path.isdir("spa_%d"%n):
            os.system("cp prod/a1.pdb spa_%d"%n)
            os.system("cp prod/rec.pdb spa_%d"%n)
            os.system("cp lig_shift.pdb spa_%d/a1_lig.pdb"%n)
            os.system("cp %s/para/SPA.amoeba.para spa_%d/SPA.para"%(os.environ['SPAHOME'],n))
            ofp.write("cd spa_%d\n"%n)
            ofp.write("%s/bin/SPA_main SPA.para\n"%os.environ['SPAHOME'])
            ofp.write("cd ..\n")
            pass
        else:
            break
        n += 1

