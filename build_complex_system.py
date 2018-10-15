#!/usr/bin/python
import sys,os
import fpdb

rec = sys.argv[1]
lig = sys.argv[2]
ligname = lig[:3]
name = ligname

os.system("mkdir %s"%name)
os.system("cp %s %s %s"%(rec,lig,name))

os.chdir(name)


# rec topology
os.system("fixhisname %s out.pdb"%rec)
os.system("addter.py out.pdb addter.pdb")
os.system("mv addter.pdb %s"%rec)
os.system("rm out.pdb")
os.system("echo 5 > 51")
os.system("echo 1 >> 51")
os.system("echo   >> 51")
os.system("gmx pdb2gmx -f %s -o rec.gro -ignh -merge all -p rec.top -i rec_posre.itp < 51 "%(rec,))
os.system("rm  51")

# lig topology
# os.system("acpype.py  -i %s"%lig)
lig_head_lines = list()
lig_body_lines = list()

body_flag = False
for line in open("%s.acpype/%s_GMX.itp"%(ligname,ligname)):
    if 'moleculetype' in line:
        body_flag = True 
    if body_flag :
        lig_body_lines.append(line)
    else:
        lig_head_lines.append(line)


# complex coordinate
os.system("gmx editconf -f rec.gro -o tmp_rec.pdb")
os.system("gmx editconf -f %s.acpype/%s_GMX.gro -o %s.acpype/%s_GMX.pdb"%(ligname,ligname,ligname,ligname))
with open('com.pdb','w') as ofp:
    for line in open("tmp_rec.pdb"):
        if line[:3] == 'END':
            break
        ofp.write(line)
    for line in open("%s.acpype/%s_GMX.pdb"%(ligname,ligname)):
        if len(line) >6 and line[:6] in ("ATOM  ","HETATM"):
            ofp.write(line)
    ofp.write("TER   \n")
    ofp.write("END   \n")

# complex topology
insert_flag = False
with open('topol.top','w') as ofp:
    for line in open('rec.top'):
        if 'moleculetype' in line:
            insert_flag = True
        if insert_flag :
            for lline in lig_head_lines :
                ofp.write(lline)
            for lline in lig_body_lines:
                ofp.write(lline)
            insert_flag = False
        ofp.write(line)
    ofp.write("%s    1\n"%ligname)

# copy files
os.system("cp -r ~/mdp ./")


# run.sh 
with open ("run.sh",'w') as ofp:
    ofp.write("#$ -S /bin/bash\n")
    ofp.write("#$ -cwd\n")
    ofp.write("#$ -e err_log\n")
    ofp.write("#$ -o out_log\n")
    ofp.write("#$ -l ngpus=2\n")
    ofp.write("#$ -q cuda\n")
    ofp.write("#$ -N N%s\n"%ligname)
    ofp.write("\n")
    ofp.write("source /usr/bin/startcuda.sh\n")
    ofp.write("\n")
    ofp.write("source /pubhome/cuda_soft/gromacs2018/bin/GMXRC.bash\n")
    ofp.write("\n")
    ofp.write("gmx editconf -f com.pdb -o box.gro -d 1.0\n")
    ofp.write("gmx grompp -f mdp/em.mdp -o em_rec.tpr -c box.gro -r box.gro -p topol.top -maxwarn 10\n")
    ofp.write("gmx mdrun -deffnm em_rec -ntmpi 1 \n")
    ofp.write("gmx solvate -cp em_rec.gro -o sys.pdb -cs -p topol.top \n")
    ofp.write("gmx grompp -f mdp/em.mdp -o tmp.tpr -c sys.pdb -r sys.pdb -p topol.top -maxwarn 10\n")
    ofp.write("echo SOL > tmp_SOL\n")
    ofp.write("echo >> tmp_SOL\n")
    ofp.write("gmx genion -s tmp.tpr -o sys_ion.pdb -p topol.top -neutral < tmp_SOL\n")
    ofp.write("mv sys_ion.pdb sys.pdb\n")
    ofp.write("gmx grompp -f mdp/em.mdp -o em.tpr -c sys.pdb -r sys.pdb -p topol.top -maxwarn 10\n")
    ofp.write("gmx mdrun -deffnm em -ntmpi 1 \n")
    ofp.write("\n")
    ofp.write("gmx grompp -f mdp/nvt.mdp -o nvt.tpr -c em.gro -r em.gro -p topol.top -maxwarn 10 \n")
    ofp.write("gmx mdrun -deffnm nvt -ntmpi 1\n")
    ofp.write("\n")
    ofp.write("gmx grompp -f mdp/npt.mdp -o npt.tpr -c nvt.gro -r em.gro -t nvt.cpt -p topol.top -maxwarn 10 \n")
    ofp.write("gmx mdrun -deffnm npt -ntmpi 1\n")
    ofp.write("\n")
    ofp.write("gmx grompp -f mdp/prod.mdp -o prod.tpr -c npt.gro -r em.gro -t npt.cpt -p topol.top -maxwarn 10 \n")
    ofp.write("gmx mdrun -deffnm prod -ntmpi 1\n")
    ofp.write("\n")
    ofp.write("cp pbsa.restr.itp rec_posre.itp\n")
    ofp.write("gmx grompp -f mdp/prod2.mdp -o prod2.tpr -c prod.gro -r em.gro -t prod.cpt -p topol.top -maxwarn 10 \n")
    ofp.write("gmx mdrun -deffnm prod2 -ntmpi 1\n")
    ofp.write("\n")
    ofp.write("source /usr/bin/end_cuda.sh\n")


## pbsa 
if True:
    origin_lig = '%s.acpype/%s_GMX.pdb'%(ligname,ligname)
    origin_rec = 'rec.gro'
    box = 'box.gro'

    ## lig.pdb
    origin_line = open(origin_rec).readlines()[2]
    box_line = open(box).readlines()[2]
    ox = float(origin_line[20:28])
    oy = float(origin_line[28:36])
    oz = float(origin_line[36:44])
    bx = float(box_line[20:28])
    by = float(box_line[28:36])
    bz = float(box_line[36:44])
    lig_o = fpdb.fPDB(origin_lig).topology.residues[0]

    for atom in lig_o.atoms:
        x,y,z = atom.posi[:3]
        x += 10*(bx-ox)
        y += 10*(by-oy)
        z += 10*(bz-oz)
        atom.posi = (x,y,z)
    lig_o.write_pdb(open('lig.pdb','w'))

    ## restr_rec.itp
    with open("pbsa.restr.itp",'w') as ofp:
        ofp.write("[ position_restraints ]\n")
        ofp.write("; atom  type      fx      fy      fz \n")
        pdb = fpdb.fPDB("com.pdb")
        for resi in pdb.topology.residues:
            if resi.name in fpdb.standard_protein_residues:
                if fpdb.dist_resi_resi_2(resi,lig_o) > 144 :
                    for atom in resi.atom:
                        if atom.element != 'H' :
                            ofp.write("%d 1 1000 1000 1000 \n"%atom.index)


os.chdir("..")
