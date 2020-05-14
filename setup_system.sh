#!/bin/bash

mkdir $1
cp rec.pdb $1
cp lp.pdb $1
cp lig.pdb $1

scp -r $1 x254:~/
ssh x254 "cd $1;/home/qyfu/Software/prepare_membrane.sh"
scp -r x254:~/$1/2_md ./$1\_md 
scp -r x254:~/$1/2_md z:/pubhome/qyfu02/GPCR_mix_solvent/mix_solvent/systems/$1\_md 
ssh x254 "rm -r $1"

cp -r $1\_md /home/fuqy/work/SPA_database_systems/GPCR/systems/

echo 'Done'


