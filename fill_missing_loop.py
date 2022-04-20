#!/usr/bin/env python
from modeller import *
from modeller.automodel import *
import argparse
import os, sys

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, required=True, help = "Input PDB")
parser.add_argument('-f', type=str, required=True, help = "Reference Fasta")
parser.add_argument('-n', type=str, required=True, help = "Protein Name")
parser.add_argument('--number', type=int, required=False, help = "Number of Models", default=5 )
args = parser.parse_args()

infile = args.i
name = args.n
fastafile = args.f
number = args.number

if not os.path.isfile(f"{name}.pdb") :
    os.system(f"cp {infile} {name}.pdb")

e = Environ()
m = Model(e, file=infile)
aln = Alignment(e)
aln.append_model(m, align_codes=name)
aln.write(file=name + '.seq')

with open("self_align_in.ali",'w') as ofp:
    for line in open(name + '.seq'):
        ofp.write(line)
    ofp.write(f">P1;{name}_fill\n")
    ofp.write("sequence:::::::::\n")
    lines = open(fastafile).readlines()[1:]
    for line in lines[:-1]:
        ofp.write(line)
    ofp.write( lines[-1].strip() + "*\n" )

# log.verbose()
env = Environ()
env.io.atom_files_directory = ['.', '../atom_files']

aln = Alignment(env, file="self_align_in.ali")

aln.salign(overhang=30, gap_penalties_1d=(-450, -50),
           alignment_type='tree', output='ALIGNMENT')

aln.write(file='self_align_out.ali', alignment_format='PIR')

a = LoopModel(env, alnfile = 'self_align_out.ali',
              knowns = name, sequence = name+"_fill" )
a.starting_model= 1
a.ending_model  = 1

a.loop.starting_model = 1
a.loop.ending_model   = number
a.loop.md_level       = refine.slow

a.make()

