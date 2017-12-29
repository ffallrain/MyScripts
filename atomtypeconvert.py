#!/usr/bin/python
import sys,os

# print usage if len(sys.argv)==1
if len(sys.argv)<4:
    print "Usage: $0 'a2g|g2a' in.pdb [out.pdb]"
    sys.exit()
ctype,infile,outfile=(sys.argv+["out.pdb"])[1:4]

# define a function which convert atom name e.g. "1HB2"->"HB21"
def fixatomname(str):
    if str[0].isdigit() :
        str="%4s"%(str[1:].strip()+str[0])
    return str

# Load convert table
table = dict()
if ctype == 'g2a':
    tablefile="%s/table_gmx2amb.dat"%os.environ['FQY_SCRIPT_PATH']
    water = (' O   HOH',' H1  HOH',' H2  HOH')

if ctype == 'a2g':
    tablefile="%s/table_amb2gmx.dat"%os.environ['FQY_SCRIPT_PATH']
    water = (' OW  SOL',' HW1 SOL',' HW2 SOL')


ifp=open(tablefile,"r")
for line in ifp:
    if line.strip()[0]=="#":continue
    res,oldname,newname=line.strip().split(":")[0:3]
    oldname=fixatomname(oldname)
    newname=fixatomname(newname)
    table[res,oldname]=newname

# Convert
ofp=open(outfile,"w")
ifp=open(infile,"r")

for line in ifp:
    if line[0:6]!="ATOM  " and line[0:6]!="HETATM":
        ofp.write(line)
        continue
    res=line[17:20]
    name=line[12:16]
    name=fixatomname(name)

    ## When non-solvnet
    if res not in ('HOH',"SOL",'WAT'):
        if table.has_key((res,name)):
            newname=table[res,name]
            newline="%s%s%s"%(line[:12],newname,line[16:])
        elif table.has_key(("*",name)):
            newname=table["*",name]
            newline="%s%s%s"%(line[:12],newname,line[16:])
        else:
            newline=line

    ## When water
    else:
        if 'O' in name:
            newline="%s%s%s"%(line[:12],water[0],line[20:])
        elif '1' in name:
            newline="%s%s%s"%(line[:12],water[1],line[20:])
        elif '2' in name:
            newline="%s%s%s"%(line[:12],water[2],line[20:])
        else:
            newline = line
    ofp.write(newline)
    pass


ifp.close()
ofp.close()
print "Done"
