#!/usr/bin/env python
import sys,os
import fpdb


infile = '5ht2b_human_4IB4.pdb'
infile = sys.argv[1]

protname = infile.split('_')[0]
species = infile.split('_')[1]
pdbid = infile.split('_')[2][:4].lower()

with open("list",'w') as ofp:
    ofp.write(pdbid)
    ofp.write("\n")

os.system("downloadpdb list")

seqres_lines = list()
for line in open("%s.pdb"%pdbid):
    if len(line) >= 6 and line[:6] == "SEQRES":
        seqres_lines.append(line)
        

with open("lp_input.pdb",'w') as ofp:
    for line in seqres_lines:
        ofp.write(line)
    for line in open(infile):
        ofp.write(line)

# find gap
gap_init = list()
gap_end = list()
gap_chain = list()
oldnumber = 0
kept_resis = set()
for line in open(infile):
    if len(line) >= 6 and line[:6] == "ATOM  ":
        chain = line[21]
        number = int(line[22:26])
        kept_resis.add( "%s:%d"%(chain,number) )

        if oldnumber == 0:
            oldnumber = number
        else:
            if number in (oldnumber, oldnumber + 1):
                pass
            else:
                gap_init.append(oldnumber)
                gap_end.append(number)
                gap_chain.append(chain)
            oldnumber = number
                
gap = list()
for (a,b,c) in zip(gap_init,gap_end,gap_chain):
    if b>a and b-a <=10:
        gap.append( (a,b,c) )
        for i in range(a,b):
            kept_resis.add("%s:%d"%(c,i))

with open("lp.input",'w') as ofp:
    ofp.write( "file datadir /home/fuqy/Software/plop21.0/data\n")
    ofp.write("file log lp.log\n")
    ofp.write("load pdb lp_input.pdb opt yes seqres yes het no wat no\n")
    for (a,b,c) in gap:
        ofp.write("loop predict %s:%d %s:%d\n"%(c,a,c,b) )
    ofp.write("write pdb lp_raw.pdb\n")

os.system("plop lp.input")

with open("lp.pdb",'w') as ofp:
    for line in open("lp_raw.pdb"):
        if len(line) >= 6 and line[:6] == "ATOM  ":
            chain = line[21]
            resindex = int(line[22:26])
            if "%s:%d"%(chain,resindex) not in kept_resis:
                continue
        ofp.write(line)

os.system("cp lp.pdb lp_tmp.pdb")
os.system("addter.py lp_tmp.pdb lp.pdb")
os.system("rm lp_tmp.pdb")

if os.path.isfile("lp_raw.pdb"):
    with open("lig.pdb",'w') as ofp:
        for line in open(infile):
            if len(line) >= 6 and line[:6] == "HETATM":
                ofp.write(line)
    with open("rec.pdb",'w') as ofp:
        for line in open("lp.pdb"):
            if len(line) >= 6 and line[:6] == "ATOM  ":
                ofp.write(line)
else:
    print("ERROR")


os.system("mkdir tmp_files")
os.system("mv list %s.pdb lp_input.pdb lp.input lp.log gmon.out tmp_files"%pdbid)

