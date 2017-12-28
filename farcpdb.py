#!/usr/bin/python
import sys,os
import fxyz

infile = sys.argv[1]
seqfile = sys.argv[2]
dt     = int(sys.argv[3])
assert infile[-4:] == '.arc'
assert os.path.isfile("tinker.key")
prefix = infile[:-4]

outfile = "%s.pdb"%(prefix)
#seqfile = "%s.seq"%(prefix)

tmppdb = 'TMP.pdb'
tmpseq = 'TMP.seq'
tmpxyz = 'TMP.xyz'

if os.path.isfile(tmppdb):
    os.remove(tmppdb)
if os.path.isfile(tmpxyz):
    os.remove(tmpxyz)
if os.path.isfile(tmpseq):
    os.remove(tmpseq)
os.system("cp %s %s"%(seqfile,tmpseq))

ofp = open(outfile,'w')

tmp_n = 0
for frame in fxyz.next_frame(infile):
    if tmp_n % dt == 0:
        tmpofp = open(tmpxyz,'w')
        xyz = fxyz.fXYZ(frame)
        xyz.write_xyz(tmpofp)
        tmpofp.close()
        x,y,z = xyz.box
        os.system("xyzpdb.x %s"%tmpxyz)
        h1 = 1
        for line in open(tmppdb):
            if "CONECT" not in line:
                if "HEADER" in line :
                    ofp.write("MODEL     %4d\n"%tmp_n)
                    ofp.write( "CRYST1%9.3f%9.3f%9.3f  90.00  90.00  90.00 P 1           1          \n"%(x,y,z) )
                elif "END" in line:
                    ofp.write("ENDMDL\n")
                elif "COMPND" in line:
                    pass
                elif "SOURCE" in line:
                    pass
                elif "H   HOH" in line:
                    if h1 :
                        line = line.replace("H   HOH","H1  HOH")
                    else:
                        line = line.replace("H   HOH","H2  HOH")
                    h1 = 1 - h1 
                    ofp.write(line)
                else:
                    ofp.write(line)
        os.system("rm %s"%tmppdb)
    tmp_n += 1

ofp.close()
    
