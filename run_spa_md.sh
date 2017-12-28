#$ -S /bin/bash
#$ -cwd
#$ -q infini
#$ -pe infini 8
#$ -N hivrt

source ~/.bashrc
echo `hostname`
echo `date`

export GMX='gmx'
export SYSGRO=$1
export REF=$1

# # Set up files
# cp -r ../mdp ./
# cp ../vdwradii.dat ./
# mkdir em_rec em_wat nvt npt prod
# 
# # gen top of rec
#    echo "5" > file51
#    echo "1" >> file51
#    gmx_mpi pdb2gmx -f cut.pdb -o rec.gro -ignh < file51
#    rm file51
#    gmx_mpi editconf -f rec.gro -o box.gro -d 1.0
# mv box.gro rec.gro 
# 
# # em rec
# cd em_rec/
#    gmx_mpi grompp -f ../mdp/em.mdp -o em.tpr -c ../rec.gro -p ../topol.top 
#    gmx_mpi mdrun -deffnm em 
# cd ..
# 
# # add solvent ,ion
# cd em_wat/
#    mv ../vdwradii.dat ./
#    gmx_mpi solvate -cp ../em_rec/em.gro -cs -o sys.gro -p ../topol.top 
#    rm vdwradii.dat
#    gmx_mpi grompp -f ../mdp/em.mdp -o em.tpr -c sys.gro -p ../topol
# echo '13' > file13
#    gmx_mpi genion -s em.tpr -o sys_ion.gro -p ../topol.top -neutral  < file13
# rm file13

# em sys
mkdir em
cd em
   $GMX grompp -f ../mdp/em.mdp -o em.tpr -c ../$SYSGRO -p ../topol.top 
   $GMX mdrun -deffnm em
cd ..

# nvt
mkdir nvt
cd nvt/
   $GMX grompp -f ../mdp/nvt.mdp -o nvt.tpr -c ../em/em.gro -p ../topol.top -r ../$REF -maxwarn 10
   $GMX mdrun -deffnm nvt 
cd ..

# npt
mkdir npt
cd npt/
   $GMX grompp -f ../mdp/npt.mdp -o npt.tpr -c ../nvt/nvt.gro -p ../topol.top -t ../nvt/nvt.cpt  -r ../$REF -maxwarn 10
   $GMX mdrun -deffnm npt
cd ..

# prod
mkdir prod
cd prod
   $GMX grompp -f ../mdp/prod.mdp -o prod.tpr -c ../npt/npt.gro -p ../topol.top -t ../npt/npt.cpt -maxwarn 10
   $GMX mdrun -deffnm prod
cd ..

# Clean
rm *#
rm */*#

echo 'Done'
echo `date`
