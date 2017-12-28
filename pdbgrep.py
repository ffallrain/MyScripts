#!/usr/bin/python
import sys,os

print " Not finished yet ! res_for_grep"

# Usage
if True:
    usage= '''
    Usage : $0 ligfile infile [radius] [res_for_grep] > outfile
    default radius 5.0 A
    default residues : all
    '''

    if len(sys.argv)<=2:
        print usage
        sys.exit()
    else:
        ligfile = sys.argv[1]
        infile = sys.argv[2]

    if len(sys.argv) >3 :
        around = float(sys.argv[3]) # Angstrm
    else:
        around = 5.0 
    
    if len(sys.argv) > 4:
        resi_to_grep = sys.argv[4]

def dist_2(a,b):
    return (a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2

def res_dist_2( resa,resb ):
    dist = min( [ dist_2( a,b ) for a in resa for b in resb ] )
    return dist

def next_res(model):
    current = None
    res = list()
    index = 0 
    for line in model:
        if len(line)>5 and line[:6] in ('ATOM  ','HETATM'):
            resn = line[17:20]
            chain = line[21]
            resi = int(line[22:26])
            index = (resn,chain,resi)
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            if index == current or current == None :
                res.append((x,y,z,line))
                current = index
            else:
                yield index,res
                res = list()
                res.append((x,y,z,line))
                current = index
        # elif 'MODEL' in line:
        #     n = int(line.split()[1])
        #     yield n,'HEAD'
        # elif 'ENDMDL' in line:
        #     yield None,'END'
    yield index,res

### Next model
n = 1
def next_model(ifp):
    global n
    model = list()
    for line in ifp:
        if 'HEADER' in line or 'MODEL' in line :
            model = list()
            n_model = n
        elif 'END' in line:
            yield n_model,model
            n += 1
        else:
            model.append(line)

### select ref
ref_coords = list()
for index, res in next_res(open(ligfile)):
    # if index[0] == ref_resn :
    if True:
        ref_coords.extend(res)
# print ref_coords

### load resi
ifp = open(infile)
for n_model,model in next_model(ifp):
    print "MODEL  %d"%n_model
    for index, res in next_res(model):
        if res_dist_2(res,ref_coords) < around**2 :
            for atom in res:
                print atom[3],
    print "ENDMDL"
ifp.close()
