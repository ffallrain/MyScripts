#!/usr/bin/python
import sys,os
import fpdb

watermodel = sys.argv[1]

origin_lig = 'lig.pdb'
origin_rec = 'rec.pdb'
box = 'box.gro'

box = sys.argv[4]
origin_para = '/home/fuqy/Software/SPA/SPA1.5/para/SPA.para'
gmx = 'gmx'
trajfile = 'traj.pdb'
syspdb = 'g1.pdb'
recpdb = 'rec.pdb'
ligfile = 'g1_lig.pdb'



para = 'SPA.para'

if not os.path.isdir('spa'):
    os.mkdir('spa')
os.chdir('spa')

os.system("echo 0 > 0")
os.system("echo >> 0 ")
os.system( "%s traj -s ../prod.tpr -f ../prod.trr -oxt %s < 0"%(gmx,trajfile) )
os.system("rm 0")

for model in fpdb.next_frame(trajfile):
    ofp = open(syspdb,'w')
    for line in model:
        ofp.write(line)
    ofp.close()

    ofp = open(recpdb,'w')
    for line in model:
        if 'SOL' not in line and 'HOH' not in line and 'WAT' not in line:
            ofp.write(line)
    ofp.close()
    break

ofp = open(para,'w')
for line in open(origin_para):
    line.replace('tip4p',watermodel)
    line.replace('g1.pdb',syspdb)
    line.replace('rec.pdb',recpdb)
    ofp.write(line)
ofp.close()

print 'Done.'


