#!/usr/bin/env python
import parmed as pmd
import sys,os

system = pmd.load_file("topol/topol.top")
system.write('combine.top.tmp', combine='all',itp=False)


with open('topol/combine.top','w') as ofp:
    writed = False
    typewrited = False
    for line in open("combine.top.tmp"):
        
        if "[ atomtypes ]" in line and not typewrited:
            ofp.write("[ atomtypes ]\n")
            ofp.write("Cl          17      35.45    0.0000  A   4.40104e-01  4.18400e-01\n")
            ofp.write("Na          11      22.99    0.0000  A   3.32840e-01  1.15897e-02\n")
            ofp.write(line)
            typewrited = True

        elif "[ moleculetype ]" in line and not writed:

            ofp.write("; Include water topology\n")
            ofp.write("#include \"amber99sb.ff/tip3p.itp\"\n")
            ofp.write("\n")
            ofp.write("#ifdef POSRES_WATER\n")
            ofp.write("; Position restraint for each water oxygen\n")
            ofp.write("[ position_restraints ]\n")
            ofp.write(";  i funct       fcx        fcy        fcz\n")
            ofp.write("   1    1       1000       1000       1000\n")
            ofp.write("#endif\n")
            ofp.write("[ moleculetype ]\n")
            ofp.write("; molname       nrexcl\n")
            ofp.write("CL              1\n")
            ofp.write("[ atoms ]\n")
            ofp.write("; id    at type         res nr  residu name     at name  cg nr  charge\n")
            ofp.write("1       Cl              1       CL              CL       1      -1.00000\n")
            ofp.write("[ moleculetype ]\n")
            ofp.write("; molname       nrexcl\n")
            ofp.write("NA              1\n")
            ofp.write("[ atoms ]\n")
            ofp.write("; id    at type         res nr  residu name     at name  cg nr  charge\n")
            ofp.write("1       Na              1       NA              NA       1      1.00000\n")
            ofp.write(line)
            writed = True
        else:
            ofp.write(line)
    
    
