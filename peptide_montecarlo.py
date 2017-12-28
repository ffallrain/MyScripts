#!/usr/bin/python
import sys,os
import math
import numpy as np
import random
from copy import deepcopy

KB = 1.3806488e-20/4.18 # kcal/K
NA = 6.02e27 #
T  = 298.               # K
Const = KB * NA / T

atoms  = list()
coords = dict()  # 1:(x,y,z,name)
template_lines = dict()
rbonds_list = list()
rbonds_left = list()
rbonds_right = list()
rbonds_matrix = list()

def dot( a, m ):
    matrix = np.array(m)
    (I,J) = matrix.shape
    prod = np.zeros( (len(a) ) ) 
    try:
        for i in range(3):
            for j in range(3):
                prod[i] = prod[i] + a[j]*matrix[j][i]
    except:
        print "Dot error"
        sys.exit(1)
    return prod

def make_matrix( x,y,z,theta):
    costt = math.cos(theta)
    sintt = math.sin(theta)
    matrix = [ [ costt+(1-costt)*x*x  , (1-costt)*x*y-sintt*z, (1-costt)*x*z+sintt*y ],
               [ (1-costt)*y*x+sintt*z, costt+(1-costt)*y*y  , (1-costt)*y*z-sintt*x ],
               [ (1-costt)*z*x-sintt*y, (1-costt)*z*y+sintt*x,  costt+(1-costt)*z*z  ] ]
    matrix = np.array(matrix)
    return matrix

def build_matrix( c1, c2 , theta ):
    x1,y1,z1 = c1[:3]
    x2,y2,z2 = c2[:3]
    dx = x1-x2
    dy = y1-y2
    dz = z1-z2
    mod = math.sqrt( dx*dx + dy*dy + dz*dz )
    matrix = make_matrix( dx/mod,dy/mod,dz/mod,theta )
    return matrix

def rotate_atom( coord, c1 , matrix ):
    x,y,z = coord[:3]
    x0,y0,z0 = c1[:3]
    dx,dy,dz = x-x0,y-y0,z-z0
    nx,ny,nz = dot( (dx,dy,dz), matrix ) 
    return nx+x0,ny+y0,nz+z0

def rotate_peptide( coords,rbond_index,theta ):
    rbond = rbonds_list[rbond_index]
    left = rbonds_left[rbond_index]
    c1 = coords[rbond[0]]
    c2 = coords[rbond[1]]
    matrix = build_matrix(c1,c2,theta)
    new_coords = dict()
    for atom in atoms:
        c = coords[atom]
        if atom in left:
            nc = rotate_atom( c, c1, matrix )
        else:
            nc = c
        new_coords[atom] = nc
    return new_coords

def read_coords(infile):
    global coords 
    for line in open(infile):
        if len(line)<6 or line[0:6] not in ('HETATM',"ATOM  "):
            continue
        else:
            atomname = line[12:16].strip()
            index = int(line[6:11])
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            template = line[:30]+"%8.3f%8.3f%8.3f"+line[54:]
            atoms.append(index)
            coords[index] = ( x,y,z,atomname )
            template_lines[index] = template
    pass

def write_coords(coords,outfile):
    ofp = open(outfile,"w")
    for index,value in coords.iteritems():
        x,y,z = value[:3]
        line = template_lines[index]%(x,y,z)
        ofp.write(line)
    ofp.close()
    return 
    
def gen_rbonds_list(coords):
    global rbonds_list
    global rbonds_left
    global rbonds_right
    global rbonds_matrix
    left = []
    right = atoms[:]

    for index in atoms:
        left.append(index)
        right.remove(index)
        x,y,z = coords[index][0:3]
        atomname = coords[index][3]

        if atomname == 'N':
            for _ in right:
                if coords[_][3] == 'CA':
                    index2 = _
                    rbonds_list.append( (index,index2) )
                    rbonds_left.append( left[:] )
                    rbonds_right.append( right[:] )
                    break
        if atomname == 'CA':
            for _ in right:
                if coords[_][3] == 'C':
                    index2 = _
                    rbonds_list.append( (index,index2) )
                    rbonds_left.append( left[:] )
                    rbonds_right.append( right[:] )
                    break
    return 

def get_potential(coords):
    tmpfile = '___tmpfile.pdb'
    tmpsnapshot = '___tmpsnapshot.pdb'
    tmplog = '___tmp.log'
    write_coords(coords,tmpfile)
    os.system('cat before.pdb %s after.pdb > %s'%(tmpfile,tmpsnapshot))
    os.system('mdrun -s calc.tpr -rerun %s -g %s >/dev/null  2>&1'%(tmpsnapshot,tmplog))
    os.system("rm *#")

    flag = False
    for line in open(tmplog):
        if flag :
            potential = float(line.split()[0])
            break
        if 'Potential' in line and  'Kinetic' in line :
            flag = True
    return potential

def get_extra_force(coords):
    k = 1
    xg = 61.855
    yg = 40.055
    zg = 44.525
    extra = 0.
    for coord in coords.values():
        x,y,z = coord[:3]
        _ = k * ( (x-xg)*(x-xg) + (y-yg)*(y-yg) + (z-zg)*(z-zg) )
        extra = extra + _
    return extra
    
def get_energy(coords):
    #return get_potential(coords) + get_extra_force(coords)
    return get_extra_force(coords)

def acceptance_ratio(delta_energy):
    if delta_energy<0:
        return True
    ratio = min(1,math.exp(-delta_energy/Const) )
    r = random.random()
    return r<ratio
    
def write_traj(trajfile,coords):
    tmpfile = '___tmpfile.pdb'
    write_coords(coords,tmpfile)
    os.system('cat before.pdb %s after.pdb >> %s'%(tmpfile,trajfile))
    return 

def sample_new_pose(coords):
    rbond_index = random.randrange(len(rbonds_list))
    theta = random.random()*2*math.pi
    return rotate_peptide(coords,rbond_index,theta)

def monte_carlo(steps, trajfile):
    old_ene = get_energy(coords)
    old_coords = deepcopy(coords)
    for i in range(steps):
        if True:
            rbond_index = random.randrange(len(rbonds_list))
            theta = random.random()*2.0*math.pi
            new_coords = rotate_peptide(coords,rbond_index,theta)
        for _ in range(3):
            rbond_index = random.randrange(len(rbonds_list))
            theta = random.random()*2.0*math.pi
            new_coords = rotate_peptide(new_coords,rbond_index,theta)
        new_ene = get_energy(new_coords)
        if acceptance_ratio(new_ene - old_ene):
            old_ene = new_ene
            write_traj(trajfile,new_coords)
            print "STEP %8d  OLD_ENE %20.3f  NEW_ENE %20.3f BOND_INDEX %3d ANGLE %4.2f  ACCEPTED WRITE TRAJ"%(i,old_ene,new_ene,rbond_index,theta)
            sys.stdout.flush()
            continue
        else:
            old_coords = deepcopy(new_coords)
            print "STEP %8d  OLD_ENE %20.3f  NEW_ENE %20.3f BOND_INDEX %3d ANGLE %4.2f  REJECTED           "%(i,old_ene,new_ene,rbond_index,theta)
            sys.stdout.flush()

# if __name__ == '__main__':
#     infile = sys.argv[1]
#     trajfile = sys.argv[2]
#     steps = 40000
#     read_coords(infile)
#     gen_rbonds_list(coords)
#     monte_carlo(steps = steps , trajfile = trajfile )
   
def test3():
    result = list()
    for i in range(100000):
        N = random.randrange(-10000,10000)
        result.append( acceptance_ratio(N) )
    print "True " , result.count(True)
    print "False " , result.count(False)

def test2():
    for j in range(1):
        infile = sys.argv[1]
        read_coords(sys.argv[1])
        gen_rbonds_list(coords)
        rbond_index = 5*j+4
        for i in range(20):
            theta = 2*math.pi*i/20.
            new_coords = rotate_peptide(coords,rbond_index,theta)
            number = get_energy(new_coords)
            print number
            write_coords(new_coords,infile+'test%d.pdb'%i)
        infile = infile + 'test7.pdb'

def test():
    atom = (10,2,7)
    x1,y1,z1 = c1 = (1,2,3)
    x2,y2,z2 = c2 = (4,5,6)
    
    template_C = 'ATOM      1  C   XXX     1    %8.3f%8.3f%8.3f  1.00 16.74           C'
    template_O = 'ATOM      1  O   XXX     1    %8.3f%8.3f%8.3f  1.00 16.74           O'
    template_N = 'ATOM      1  N   XXX     1    %8.3f%8.3f%8.3f  1.00 16.74           N'

    mod = math.sqrt( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 )
    for i in range(100):
        ratio = ((3)-(-3))*i/100. + ( -3 )
        x = ratio*x1 + (1-ratio)*x2
        y = ratio*y1 + (1-ratio)*y2
        z = ratio*z1 + (1-ratio)*z2
        print template_C%(x,y,z)
    
    for i in range(100):
        i = 10*mod*(i-50)/100
        print template_O%(i,0,0)
        print template_O%(0,i,0)
        print template_O%(0,0,i)
    
    for i in range(100):
        theta = 2*math.pi*i/100.
        matrix = build_matrix( c1,c2,theta )
        prod = rotate_atom(atom,c1,matrix)
        print template_N%tuple(prod)

test2()
