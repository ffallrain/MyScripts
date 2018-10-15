#$ -S /bin/bash
#$ -cwd
#$ -q katyusha 
#$ -pe katyusha 4

source /opt/gromacs504/bin/GMXRC.bash 
source ~/.bashrc

gmx_mpi  make_ndx -f prod.gro -o index.ndx <<eof
q
eof
g_mmpbsa -f pbsa.trr -s prod.tpr -n index.ndx -pdie 2 -decomp -dt 100 <<eof
1
13
eof
g_mmpbsa -f pbsa.trr -s prod.tpr -n index.ndx -pdie 2 -decomp -i /pubhome/qyfu02/software/g_mmpbsa/bin/polar.mdp  -nomme -pbsa -dt 100 <<eof
1
13
eof
g_mmpbsa -f pbsa.trr -s prod.tpr -n index.ndx -pdie 2 -decomp -i /pubhome/qyfu02/software/g_mmpbsa/bin/apolar_sasa.mdp  -nomme -pbsa -apol sasa.xvg -apcon sasa_contrib.dat -dt 100 <<eof
1
13
eof
MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg 

cd ..
