#!/usr/bin/python
import math
import simtk.openmm.app as soa
import simtk.unit as su
import sys,os

MAX = 99999
TMPFILE = "FPDB.SOA.TMPPDBFILE.PDB"
kJ_to_kcal = 1/4.184

if True: ### residue names 
    standard_protein_residues = ('ARG','LYS','HIS','HIP','HIE',
         'HID','ASP','GLU',
         'ASN','GLN','SER','THR','CYS','CYX','GLY','PRO','ALA',
         'VAL','LEU','ILE','MET','PHE','TYR','TRP' )

    standard_water_redsidues = ('HOH','SOL','WAT')

    protein_hbond_donors = (
        ('*','N','H'),
        ('*','N','HN'),
        ('ARG', 'NE','HE'),
        ('ARG','NH1','HH11'),
        ('ARG','NH1','HH12'),
        ('ARG','NH2','HH21'),
        ('ARG','NH2','HH22'),
        ('LYS', 'NZ', 'HZ1'),
        ('LYS', 'NZ', 'HZ2'),
        ('LYS', 'NZ', 'HZ3'),
        ('HIS','ND1', 'HD1'),
        ('HIS','NE2', 'HE2'),
        ('HIP','ND1', 'HD1'),
        ('HIP','NE2', 'HE2'),
        ('HID','ND1', 'HD1'),
        ('HIE','NE2', 'HE2'),
        ('ASN','ND2','HD21'),
        ('ASN','ND2','HD22'),
        ('GLN','NE2','HE22'),
        ('GLN','NE2','HE21'),
        ('SER','OG','HG'),
        ('THR','OG1','HG1'),
        ('CYS','SG','HG'),
        ('TYR','OH','HH'),
        ('TRP','NE1','HE1'),
    )

if True: ### Global varieties 
    newnew = '/home/fuqiuyu/.ffallrain/newnew'
    TMPFILE = 'FIND_RING.PDB'
    TMPFILE_MOL2 = 'FIND_RING.mol2'
    babel = '/usr/bin/babel'

class framePDB( soa.PDBFile ):
    def __init__(self,frame):
        if hasattr(frame,'isalpha'):
            soa.PDBFile.__init__(self,frame) ## here frame is the name of pdbfile
        else:
            ofp = open(TMPFILE,'w')
            for line in frame:
                ofp.write(line)
            ofp.close()
            soa.PDBFile.__init__(self,TMPFILE)
            os.remove(TMPFILE)

    def find_rec_hbond_acceptors(self):
        acceptors = list()
        residues = self.topology.residues()
        for residue in residues:
            if residue.name in standard_protein_residues:
                for atom in residue.atoms():
                    ##### Oxygen in protein. all could be regareded as hbond receptor
                    if atom.element.symbol == 'O':
                        acceptors.append( self.positions[atom.index] )
                    ##### Nitrogen in protein. Only those in Imidazole ring are considered
                    elif atom.element.symbol == 'N' :
                        if residue.name in ('HIS','HID','HIP','HIE'):
                            if atom.name not in ('NH','N'):
                                acceptors.append( self.positions[atom.index] )
                    ##### sulfide ignored. 
                    elif atom.element.symbol == 'S':
                        pass
        return acceptors

    def find_atom(self,residue,atomname):
        for atom in residue.atoms():
            if atom.name == atomname:
                return atom.index
        return None

    def find_rec_hbond_donors(self):
        donors = list()
        residues = self.topology.residues()
        for residue in residues:
            if residue.name in standard_protein_residues:
                for template in protein_hbond_donors:
                    rname,dname,hname = template
                    if residue.name == rname or rname == '*':
                        d_index = self.find_atom(residue,dname)
                        h_index = self.find_atom(residue,hname)
                        if d_index and h_index:
                            donor = self.positions[d_index],self.positions[h_index]
                            donors.append(donor)
                    else:
                        pass
        return donors

    def _find_res_name( self,resi, top ):
        name = None
        res_atom_list = set()
        for atom in resi.atoms():
            res_atom_list.add(atom.name)
        for topresi in top.get_resilist():
            top_res_atom_list = None
            top_res_atom_list = set( [x[0] for x in top.get_resi(topresi)] )
            if top_res_atom_list == res_atom_list:
                name =  topresi
                break
        return name

    def load_ff_params(self, top ):
        self._params = dict()
        for resi in self.topology.residues():
            #load residue parameters
            name = self._find_res_name(resi,top)

class fATOM():
    def __init__(self,atom_line):
        tmpname = atom_line[12:16]
        if tmpname[0] in "0123456789" and tmpname[3]!=" ":
            tmpname = tmpname[1:] + tmpname[0]
        tmpname = tmpname.strip()
        self.name = tmpname
        self.charge = None
        self.sig = None
        self.eps = None
        self.index = int(atom_line[6:11])
        x = float(atom_line[30:38])
        y = float(atom_line[38:46])
        z = float(atom_line[46:54])
        self.posi = (x,y,z)
        self.connect_count = 0 ## for bond
        self.bond = list()

    def addparm(self,charge,sig,eps):
        self.charge = charge
        self.sig = sig
        self.eps = eps

    def _addconnect(self):
        self.connect_count += 1

    def _delconnect(self):
        self.connect_count -= 1
        if self.connect_count < 0 :
            sys.stderr.write("WARNING,BOND CONNECTION LESS THAN ZERO.\n")
    def addbond(self,bond):
        self.bond.append(bond)
        self._addconnect()
    def delbond(self,bond):
        self.bond.remove(bond)
        self._delconnect()

class fCHEMO():
    @staticmethod
    def _next_atom_line(resi_lines):
        for atom_line in resi_lines:
            if len(atom_line)>=6 and atom_line[:6] in ('HETATM','ATOM  '):
                yield atom_line
    def __init__(self,resi_lines):
        assert len(resi_lines) > 0
        self.name = resi_lines[0][17:20].strip()
        self.index = int(resi_lines[0][22:26])
        self.insertion = resi_lines[0][26]
        self.atoms = list()
        self.index_shift = 0
        for atom_line in fRESIDUE._next_atom_line(resi_lines):
            self.atoms.append( fATOM(atom_line) )
        if len(self.atoms)>0:
            self.index_shift = self.atoms[0].index - 1
        else:
            self.index_shift = 0
    def find_atoms(self, name = None , index = None ):
        result = list()
        ignore_name = False
        ignore_index = False
        if name == None:
            ignore_name = True
        if index == None:
            ignore_index = True
        for atom in self.atoms:
            if ignore_name or atom.name in name:
                if ignore_index or atom.index in index:
                        result.append(atom)
        return result
    def write_pdb(self,ofile):
        if hasattr(ofile,'write'):
            ofp = ofile
            for atom in self.atoms:
                x,y,z = atom.posi
                line = 'ATOM  %5d %4s %3s  %4d    %8.3f%8.3f%8.3f  1.00  0.00\n'%(atom.index,atom.name,self.name,self.index,x,y,z)
                ofp.write(line)
        else:
            ofp = open(ofile,'w')
            for atom in self.atoms:
                x,y,z = atom.posi
                line = 'ATOM  %5d %4s %3s  %4d    %8.3f%8.3f%8.3f  1.00  0.00\n'%(atom.index,atom.name,self.name,self.index,x,y,z)
                ofp.write(line)
            ofp.close()
    def debug(self):
        print 'name',self.name
        print 'index',self.index
        print 'insertion',self.insertion
        print 'atoms:'
        for atom in self.atoms:
            print atom.name,
        print

class fRESIDUE(fCHEMO):
    pass

class fRING(fCHEMO):
    def __init__(self,atom_list):
        fCHEMO.__init__(self,[])
        for atom in atom_list:
            self.atom.append(atom)

class fBOND:
    def __init__(self,atoma,atomb):
        # print "DEBUG ADD BOND BETWEEN",atoma.name,'and',atomb.name
        if atoma.name<atomb.name:
            atoma.addbond(self)
            atomb.addbond(self)
            self._ = (atoma,atomb)
        elif atoma.name>atomb.name:
            atoma.addbond(self)
            atomb.addbond(self)
            self._ = (atomb,atoma)
        else:
            pass
            sys.stderr.write("WARNING,INTENDED TO CONNECT BOND BETWEEN IDENTICAL ATOMS\n")
    def del_me(self):
        self._[0].delbond(self)
        self._[1].delbond(self)

class fCOMPOUND(fCHEMO):
    BOND_CUTOFF_H = 1.5 # Angstrom
    BOND_CUTOFF_H_2 = 2.25 # Angstrom
    BOND_CUTOFF = 2.0 # Angstrom
    BOND_CUTOFF_2 = 4.0 # Angstrom
    def __init__(self,compound_lines):
        fCHEMO.__init__(self,compound_lines)
        self._atom_classification()
        self._makebond()
    def _atom_classification(self):
        self.h_list = list()
        self.heavy_list = list()
        for atom in self.atoms:
            if len(atom.name)>=1 and atom.name[0] == 'H' :
                self.h_list.append(atom)
            else:
                self.heavy_list.append(atom)
    def _makebond(self):
        self.bonds = set()
        self._make_h_bond()
        self._make_heavy_bond()
    def _make_h_bond(self):
        for h in self.h_list:
            for heavy in self.heavy_list:
                if dist_2(h,heavy) <= self.BOND_CUTOFF_H_2:
                    self.bonds.add(fBOND(h,heavy))
                    break
    def _make_heavy_bond(self):
        for heavy_1 in self.heavy_list:
            for heavy_2 in self.heavy_list:
                if heavy_1.name < heavy_2.name :
                    if dist_2(heavy_1,heavy_2) <= self.BOND_CUTOFF_2:
                        self.bonds.add(fBOND(heavy_1,heavy_2))
    def truncate_leaf(self):
        while True:
            to_be_deleted = list()
            for atom in self.atoms:
                assert atom.connect_count > 0
                if atom.connect_count == 1:
                    to_be_deleted.append(atom)
            if len(to_be_deleted) == 0 :
                break
            else:
                for atom in to_be_deleted:
                    bonds = atom.bond
                    for bond in bonds:
                        bond.del_me()
                        self.bonds.remove(bond)
                    self.atoms.remove(atom)
        self._atom_classification()
    def find_ring(self):
        pass
        self.write_mol2(TMPFILE_MOL2)
        answer = os.popen("%s %s "%(newnew,TMPFILE_MOL2)).readlines()
        os.remove(TMPFILE_MOL2)
        self.rings = list()
        for line in answer:
            tmpring = list()
            numbers = [ int(x)+self.index_shift for x in line.replace(',' , '').split()[2:] ]
            print numbers
            tmpring = self.find_atoms(index = numbers)
            self.rings.append(tmpring)
        return self.rings
        #analyze answer and tranlate to my class  ( fRING class )
    def write_mol2(self,ofile):
        self.write_pdb(TMPFILE)
        os.system("%s -ipdb %s -omol2 %s"%(babel,TMPFILE,ofile))
        os.system("echo '@<TRIPOS>ATOM' >> %s"%ofile)
        os.remove(TMPFILE)
    def list_connect_count(self):
        for atom in self.atoms:
            print atom.name,atom.connect_count
    def debug(self):
        fCHEMO.debug(self)
        print "Hydrogen atoms:"
        for h in self.h_list:
            print h.name,
        print "Heavy atoms:"
        for heavy in self.heavy_list:
            print heavy.name,
        print "Num of Bonds:",len(self.bonds)
        print "Atom index:"
        for atom in self.atoms:
            print atom.index,
        print
   
class fTOPOLOGY():
    @staticmethod
    def _next_resi_lines(lines):
        resi_lines = list()
        oldresindex = None
        for line in lines:
            if len(line)<6 or line[:6] not in ('ATOM  ','HETATM'):
                continue
            else:
                resindex = line[22:26].strip()+line[26]
                if resindex == oldresindex or oldresindex == None:
                    resi_lines.append(line)
                else:
                    yield resi_lines
                    resi_lines = list()
                    resi_lines.append(line)
            oldresindex = resindex
        yield resi_lines

    def __init__(self,lines):
        self.residues = list()
        for resi_lines in fTOPOLOGY._next_resi_lines(lines):
            self.residues.append( fRESIDUE(resi_lines) )

    def get_protein_residues(self):
        prot_residues = list()
        for resi in self.residues:
            if resi.name in standard_protein_residues:
                prot_residues.append(resi)
        return prot_residues

    def get_water_residues(self):
        water_residues = list()
        for resi in self.residues:
            if resi.name in standard_water_redsidues:
                water_residues.append(resi)
        return water_residues

    def find_residues(self, name = None , index = None ,atom_index = None ):
        result = list()
        ignore_name = False
        ignore_index = False
        ignore_atom_index = False
        if name == None:
            ignore_name = True
        if index == None:
            ignore_index = True
        if atom_index == None:
            ignore_atom_index = True
        for residue in self.residues:
            if ignore_name or residue.name in name:
                if ignore_index or residue.index in index:
                    if ignore_atom_index or sum( [ atom_index.count(x.index) for x in residue.atoms] ) > 0:
                        result.append(residue)
        return result
    
class fPDB:
    def __init__(self,frame):
        lines = None
        if hasattr(frame,'isalpha'):
            lines = open(frame).readlines()
        else:
            lines = frame
        
        self.topology = fTOPOLOGY(lines)

    @staticmethod
    def load_ff_param_resi(resi,gmxtop):
        resi_atoms = set( [ x.name for x in resi.atoms ] )
        for gmx_resi in gmxtop.get_resilist():
            gmx_atoms = set([ x[0] for x in gmxtop.get_resi(gmx_resi) ] )
            if resi_atoms == gmx_atoms:
                for atom in resi.atoms:
                    for gmx_atom in gmxtop.get_resi(gmx_resi):
                        if atom.name == gmx_atom[0]:
                            atom.addparm( gmx_atom[3],gmx_atom[1],gmx_atom[2] )
                return 
        print "Error loading residue parameters",resi.name,resi.index
        return

    def load_ff_params(self, gmxtop ):
        residues = list(self.topology.residues)
        for resi in residues :
            fPDB.load_ff_param_resi(resi,gmxtop)

    def check_params(self):
        for resi in self.topology.residues:
            for atom in resi.atoms:
                print atom.name,atom.charge,atom.sig,atom.eps

###### Function to compute vdw
def calc_vdw(a,b,dist_2):
    sig1,eps1=a.sig,a.eps
    sig2,eps2=b.sig,b.eps
    sig = 0.5 * ( sig1 + sig2 )
    sig = sig * sig
    eps = math.sqrt(eps1*eps2)
    _dist = dist_2 / 100.
    _ = ( sig/_dist ) ** 3
    return  4 * eps * ( _ * _ - _ ) 

###### Function to compute charge
def calc_chg(a,b,dist_2):
    #f_charge = 138.935485
    charge1 = a.charge
    charge2 = b.charge
    return 138.935485*charge1*charge2/(math.sqrt(dist_2)/10.)

###### dist_2 atom atom
def dist_2(a,b):
    x1,y1,z1 = a.posi
    x2,y2,z2 = b.posi
    return (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 

def potential_atom_atom( atoma,atomb ):
    d_2 = dist_2(atoma,atomb)
    vdw =  calc_vdw(atoma,atomb,d_2) 
    chg =  calc_chg(atoma,atomb,d_2)
    return (vdw+chg)*kJ_to_kcal

def potential_resi( resia,resib ):
    if resia == resib:
        # sys.stderr.write("WARNING, YOU ARE ATTEMPING TO COMPUTE THE POTENTIAL BETWEEN IDENTICAL RESIDUES. THE FUNCTION WILL IGNORE IT AND RETURN ZERO.\n")
        return 0
    e = 0
    for atoma in resia.atoms:
        for atomb in resib.atoms:
            e += potential_atom_atom(atoma,atomb)
    return e

def next_frame(filename):
    frame = list()
    for line in open(filename):
        if len(line)>=6 and line[:6] == "MODEL ":
            frame = list()
            frame.append(line)
        elif len(line)>=6 and line[:3] == "END":
            frame.append(line)
            yield frame
        else:
            frame.append(line)

if False:
    def dist_atom(a,b):
        return math.sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 )

    def dist_atom_resi(atom, resi):
        assert len(atom)>=3
        assert len(resi)>0
        dist = MAX
        node = None
        for atomb in resi:
            tmp = dist_atom(atom,atomb)
            if tmp < dist:
                dist = tmp
                node = atomb
        assert node != None
        return dist,node

# Test
if __name__ == '__main__':
    pass
        
