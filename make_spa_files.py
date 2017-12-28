#!/usr/bin/python
import sys,os
import fpdb

infile = sys.argv[1]

a1_file = 'a1.pdb'
lig_file = 'a1_lig.pdb'
rec_file = 'rec.pdb'

para_source = '/home/fuqiuyu/work/nmr_druggability/md/finished/1dhm/spa/SPA.para'
para_file = 'SPA.para'

print ">>>>> preparing SPA input files"

for model in fpdb.next_frame(infile):

    pdb = fpdb.fPDB(model)
    pdb.write_pdb(a1_file)
    print "----- sys pdb done."

    ofp_rec = open(rec_file,'w')
    for residue in pdb.topology.residues:
        if residue.name in fpdb.standard_protein_residues:
            residue.write_pdb(ofp_rec)
    print "----- rec pdb done."

    ofp_lig = open(lig_file,'w')
    for line in open(rec_file):
        if len(line)>=6 and line[:6] in ('ATOM  ','HETATM'):
            if line[12:16].strip() not in ('C','O','N','CA'):
                if line[13] != 'H':
                    ofp_lig.write(line)
    print "----- lig pdb done."

    break ## important !!

os.system("cp %s %s"%(para_source,para_file))
print "----- SPA.para done."

print "----- All done."
