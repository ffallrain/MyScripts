#!/usr/bin/python
import sys,os
usage="""
Add Cap Using tLEaP.
Firstly addh
Then add cap NME and ACE to the C- and N- terminal of each peptide
Usage $0 in.pdb out.pdb
"""
if len(sys.argv)<3:
    print usage
    sys.exit()
infile,outfile=sys.argv[1:3]

leap1in='''
source leaprc.ff14SB
rec = loadpdb %s
savepdb rec addcap_tmp.pdb
quit
'''
ofp=open("addcap_tleap1.in","w")
ofp.write(leap1in%infile)
ofp.close()
os.system("tleap -f addcap_tleap1.in")

firstresi=True
lastter=True
cachedlines=""
oldindex=0
ofp=open("addcap_tmp2.pdb","w")
for line in open("addcap_tmp.pdb","r"):
    if len(line)>30:index=int(line[22:26])
    if index!=oldindex:
        firstresi=lastter
    oldindex=index
    if firstresi:
        if " H1 " not in line and " H2 " not in line and " H3 " not in line :
            cachedlines=cachedlines+line
    if not firstresi:
        ofp.write(cachedlines)
        cachedlines=""
    if "OXT" in line:
        ofp.write("%s N   NME%s"%(line[:12],line[20:]))
    elif "H3 " in line:
        ofp.write("%s C   ACE%s"%(line[:12],line[20:]))
    elif not firstresi:
        ofp.write(line)
    else:
        pass
    lastter=("TER" in line)
ofp.close()

leap2in='''
source leaprc.ff14SB
rec = loadpdb addcap_tmp2.pdb
savepdb rec %s
quit
'''
ofp=open("addcap_leap2.in","w")
ofp.write(leap2in%outfile)
ofp.close()
os.system("tleap -f addcap_leap2.in")
