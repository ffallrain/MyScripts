#!/usr/bin/env python
import sys,os


t = sys.argv[1]

os.system("./make_lig_shift.py")
os.chdir("MD-%s-1"%t)

i = 0 
with open("file0",'w') as ofp:
    ofp.write("0\n")
    ofp.write("\n")

I = 0
while(True):
    i = i + 1 
    # if i >= 10 :
    #     break
    os.system(f"gmx trjconv -f step7.xtc -s step7.tpr -o {(i-1)*10}.{i*10}.traj.pdb -b {(i-1)*10000} -e {i*10000} < file0")
    if not os.path.isfile(f"{(i-1)*10}.{i*10}.traj.pdb"):
        I = i - 1 
        break
# I = 1


for i in range(I):
    if not os.path.isdir("%d.spa"%i):
        os.mkdir("%d.spa"%i)
    os.system(f"cp ../lig_shift.pdb ./{i}.spa/g1_lig.pdb")
    os.system(f"mv {i*10}.{i*10+10}.traj.pdb ./{i}.spa/traj.pdb")
    with open("fileProtein",'w') as ofp:
        ofp.write("Protein\n\n")
    os.system(f"gmx trjconv -f step6.0.gro -s step6.0.tpr -o ./{i}.spa/rec.pdb < fileProtein")
    os.system(f"gmx editconf -f step6.0.gro -o ./{i}.spa/g1.pdb ")
    os.system(f"cp /home/fuqy/Software/SPA/SPA1.5/para/SPA.para ./{i}.spa/")
    

