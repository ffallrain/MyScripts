#!/usr/bin/python
import sys,os
import fpdb 

lmp = "~/work/QEM_MD/body/sethbrin/lammps_waterbox/src/lmp_mpi"
infile = sys.argv[1]
outfile = sys.argv[2]
os.system("%s -restart %s %s -l /dev/null > /dev/null "%(lmp,infile,"tmp.data"))
infile = "tmp.data"

## load residues
if True:
    residues = dict()
    ## load centers
    flag = False
    for line in open(infile):
        if "Atoms" in line:
            flag = True
            continue
        elif 0 < len(line.split()) < 3 :
            flag = False
        else:
            pass
        if flag :
            items = line.split()
            if len(items) > 0:
                index = int(items[0])
                x = float(items[4]) * 0.1
                y = float(items[5]) * 0.1 
                z = float(items[6]) * 0.1
                water = fpdb.fRESIDUE()
                water.var1 = (x,y,z)
                water.index = index
                residues[index] = water

    ## load velocity
    flag = False 
    for line in open(infile):
        if "Velocities" in line:
            flag = True
            continue
        elif 0 < len(line.split()) < 3 :
            flag = False
        else:
            pass
        if flag :
            items = line.split()
            if len(items) > 0 :
                index = int(items[0])
                x = float(items[1]) * 100
                y = float(items[2]) * 100
                z = float(items[3]) * 100
                a = float(items[4])
                b = float(items[5])
                c = float(items[6])
                residues[index].var2 = (x,y,z,a,b,c)

    ## load coords
    pass

    ## load box lattice length
    for line in open(infile):
        if "xlo xhi" in line:
            boxx = float(line.split()[1]) - float(line.split()[0]) 
        elif "ylo yhi" in line:
            boxy = float(line.split()[1]) - float(line.split()[0])
        elif "zlo zhi" in line:
            boxz = float(line.split()[1]) - float(line.split()[0])
        else:
            pass

    ## load timestep
    for line in open(infile):
        if "timestep" in line:
            time = float(line.split()[-1]) * 0.001

## write gro
ofp = open(outfile,'w')
ofp.write("Generated by restart2gro.py t=%g\n"%time)
n = len(residues)
ofp.write("%5d\n"%n)
for i in range(n):
    water = residues[i+1]
    ofp.write( ("%5s"*4+"%8.3f"*3+"%8.4f"*3+"\n")%(i+1,'WAT  ','  O  ',i+1,water.var1[0],water.var1[1],water.var1[2],water.var2[0],water.var2[1],water.var2[2]) )
ofp.write("%8.3f%8.3f%8.3f\n"%(boxx,boxy,boxz))
ofp.close()

os.system("rm tmp.data")

