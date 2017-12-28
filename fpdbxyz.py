#!/usr/bin/python
import sys,os

prefix="FPDBXYZ."
if len(sys.argv)<3:
    print "Usage $0 parameter_file xxx.pdb [xxx.xyz]"
    sys.exit()
if len(sys.argv)<4:
    param = sys.argv[1]
    if param[-4:] == ".prm":
        param = param[:-4]
    infile=sys.argv[2]
    assert infile[-4:]==".pdb"
    outfile=infile[:-4]+".xyz"
else:
    infile,outfile=sys.argv[1:3]

##### parameter file contents
fleapin=prefix+"leap.in"
leapin='''
source leaprc.ff14SB
rec = loadpdb %s
savepdb rec %s
quit
'''
ftinkerkey="tinker.key"
tinkerkey='''
parameters %s
'''%param
fpdbxyzparam=prefix+"pdbxyzparam"
pdbxyzparam='''
%s
ALL

'''
fxyzeditparam=prefix+"xyzedit"
xyzeditparam='''
%s
19
%s


'''

##### Assert
if outfile[-4:] != ".xyz":
    print "##### The output file name doesn't end by '.xyz'. So I guess you made a mistake. STOP"
    sys.exit()
if not os.path.isfile("%s.prm"%param):
    print "There's no %s.prm, which I need. STOP"%param
    sys.exit()

##### Divide input file into rec and water
#     REC
os.system("cp %s bak.%s"%(infile,infile))
frec=prefix+'rec.pdb'
fhoh=prefix+'hoh.pdb'
os.system("grep -v HOH %s |grep -v SOL |grep -v WAT |grep -v HETATM > %s"%(infile,frec))
os.system("grep -P 'HOH|WAT|SOL' %s > %s"%(infile,fhoh))

##### convert rec by pdbxyz.x
#     wrapatomtype
#os.system("wrapatomtype %s %s"%(frec,prefix+"wrap.pdb"))
#os.system("mv %s %s"%(prefix+"wrap.pdb",frec))
#     tleap
ofp=open(fleapin,"w")
ofp.write(leapin%(frec,frec))
ofp.close()
os.system("tleap -f %s"%fleapin)
#     addter.py
os.system("addter.py %s %s"%(frec,prefix+"addter.pdb"))
os.system("mv %s %s"%(prefix+"addter.pdb",frec))
#     addchainmaker
os.system("addchainmarker %s %s"%(frec,prefix+"addcm.pdb"))
os.system("mv %s %s"%(prefix+"addcm.pdb",frec))
#     Make tinker.key
#lines=os.popen("grep CRYST1 %s"%infile).readlines()
#x=float(lines[0].split()[1])
#y=float(lines[0].split()[2])
#z=float(lines[0].split()[3])
ofp=open(ftinkerkey,"w")
ofp.write(tinkerkey)
#ofp.write(tinkerkey%(x,y,z))
ofp.close()
#     pdbxyz.x
assert frec[-4:]==".pdb"
tmp=frec[:-4]
#os.system("rm %s.xyz* "%(tmp))
#os.system("mv %s.seq %s.seq"%(tmp,infile[:-4]))
ofp=open(fpdbxyzparam,"w")
ofp.write(pdbxyzparam%(frec))
ofp.close()
status=os.system("/opt/tinker7.1/bin/pdbxyz.x < %s"%fpdbxyzparam)
assert status==0
frecxyz=tmp+".xyz"

##### convert water by hohxyz.py
#     convert
assert fhoh[-4:]==".pdb"
fhohxyz=fhoh[:-4]+".xyz"
status=os.system("hohxyz.py %s %s"%(fhoh,fhohxyz))
print ">>>>>>>",fhoh,fhohxyz
assert status==0

##### Merge by xyz.edit
#     merge
fmergexyz=prefix+"merge.xyz"
os.system("cp %s %s"%(frecxyz,fmergexyz))
ofp=open(fxyzeditparam,"w")
ofp.write(xyzeditparam%(fmergexyz,fhohxyz))
ofp.close()
status=os.system("xyzedit.x < %s"%fxyzeditparam)
assert status==0
#     rename
status=os.system("mv %s_2 %s"%(fmergexyz,outfile))
assert status==0

##### Clean
os.system("mv %s.seq %s.seq"%(frec[:-4],infile[:-4]))
os.system("rm %s*"%prefix)
