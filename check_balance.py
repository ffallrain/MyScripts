#!/usr/bin/env python
import sys,os

os.system("./make_lig_shift.py")
os.chdir("MD-1")

i = 0 
with open("file0",'w') as ofp:
    ofp.write("0\n")
    ofp.write("\n")

I = 0
# while(True):
#     i = i + 1 
#     # if i >= 10 :
#     #     break
#     os.system(f"gmx trjconv -f nptMD.xtc -s nptMD.tpr -o {(i-1)*10}.{i*10}.traj.pdb -b {(i-1)*10000} -e {i*10000} < file0")
#     if not os.path.isfile(f"{i-1}*10.{i*10}.traj.pdb"):
#         I = i - 1 
#         break
I = 6

for i in range(I):
    if not os.path.isdir("%d.cpa"%i):
        os.mkdir("%d.cpa"%i)
    os.system(f"cp ../lig_shift.pdb ./{i}.cpa/g1_lig.pdb")
    os.system(f"mv {i*10}.{i*10+10}.traj.pdb ./{i}.cpa/traj.pdb")
    with open("fileProtein",'w') as ofp:
        ofp.write("Protein\n\n")
    os.system(f"gmx trjconv -f em.gro -s em.tpr -o ./{i}.cpa/rec.pdb < fileProtein")
    os.system(f"gmx editconf -f em.gro -o ./{i}.cpa/g1.pdb ")
    os.system(f"cp /home/fuqy/Software/SPA/CPA1.5/para/CPA.para ./{i}.cpa/")
    

