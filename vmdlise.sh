#!/bin/bash

name=$1

gmx editconf -f $name.gro -o $name.pdb
<<<<<<< HEAD
gmx trjconv -f $name.trr -s $name.tpr  -o tmp.trr -pbc nojump << eof
=======
gmx trjconv -f $name.trr -s $name.tpr  -o tmp.trr -pbc cluster << eof
non-Water
>>>>>>> 94d0c8388a28aa3d1047e5f2f8964817313edfe1
System
eof

#gmx trjconv -f tmp.trr -s $name.tpr  -o tmp2.trr -center << eof
#System
#eof

#mv tmp2.trr $name\_vmd_view.trr 
#rm tmp.trr

mv tmp.trr $name\_vmd_view.trr

