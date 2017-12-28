#!/usr/bin/python
import sys,os

commands='''
open %s
open %s
mm #0 #1
write relative #0 format pdb #1 mm_tmp.pdb
stop
'''

usage='''
$0 file_reference.pdb file_to_match.pdb 
'''
if len(sys.argv)<3:
    print usage
    sys.exit()
ref,match=sys.argv[1:3]

os.system("cp %s bak_%s"%(match,match))
ofp=open("mm.com","w")
ofp.write(commands%(ref,match))
ofp.close()
os.system("chimera --nogui mm.com > chimera.log")
os.system("mv mm_tmp.pdb %s"%match)
os.system("rm mm.com")
