#!/usr/bin/python

"""
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Copyright National Institute of Biological Sciences, Beijing, 2014

Bugs to be report to:
Lifeng Zhao, zhao_lf@yeah.net

version:
0.12:	proper torsion bug for multi terms of one torion rectified.
0.13:   improper torsion bug and atom indices reading bugs are corrected.
0.14:   Atom type suffix can be added, alowing multi top files be used in one simulation.
"""

import os,sys

__ver__ = 0.14
__doc__ = """
	This codes is used to convert Schrodinger format OPLS2005 force field 
		to Gromacs format.
	A PDB file and a Schrodinger format FF file are needed.

	Usage: ./%prog [options] filename
"""

ElemMass = {'C':12.011, 'H':1.0079, 'O':15.9994, 'N':14.0067, 'F':18.9984, 
	'S':32.066, 'P':30.974, 'Cl':35.453, 'CL':35.453, 'Si':28.0855, 'Br':79.904, 'Na':22.990, 'I':126.9}

def read_args():
	if len(sys.argv)==1:
		print __doc__
		raise Exception, "Wrong arguments. Try -h."

        from optparse import OptionParser
        parser = OptionParser(usage=__doc__,
                              version="%prog"+str(__ver__))
        parser.add_option('-f', '--input',
                          action='store',
                          dest='inputname',
                          help='PDB structure file name.')
        parser.add_option('-o', '--output',
                          action='store',
                          dest='outputname',default='',
                          help='Name of Gromacs topology output file.')
        parser.add_option('-p', '--top',
                          action='store',
                          dest='topname',default='',
                          help='Schrodinger FF file')
        parser.add_option('-i', '--suffix',
                          action='store',
                          dest='suffix',default=0,
                          help='suffix for atom types, 0 means no suffix. Default:0')
        (options, args) = parser.parse_args()
        return (options, args)

class top_atom():
	def __init__(self, linelist, father, suf=0):
		self.ndx = int(linelist[0])

		if int(linelist[1])>0:
			father.add_connection(self.ndx, int(linelist[1]))

		self.temp1 = linelist[2]

		self.name = linelist[3]
		self.atype = linelist[4].strip('_')
		if suf: self.atype += '_'+str(suf)
		self.old_ndx = int(linelist[5])

		self.bond = float(linelist[6])
		self.angle = float(linelist[7])
		self.tors = float(linelist[8])

class pdb_atom():
	def __init__(self, line, father):
		resname = line[16:20].strip()
		resndx = int(line[22:26])
		if len(father.pdb_atoms)==0: pass
		elif resname!=father.pdb_atoms[1].resname or \
			resndx!=father.pdb_atoms[1].resndx:
			raise Exception, 'More than one group in pdb found.'

		self.name = line[11:16].strip()
		elem = line[12:14].strip()
		if elem[0] in '0123456789': elem = elem[1]
		self.elem = elem
		self.resname = resname
		self.resndx = resndx
		self.x = [float(line[30:38]),float(line[38:46]),float(line[46:54])]

class ff_nonbond():
	def __init__(self, line):
		temp = line.split()
		self.ndx = int(temp[0])
		self.sig = float(temp[1])
		self.eps = float(temp[2])
		self.q = float(temp[3])

class ff_bond():
	def __init__(self, line, father):
		line = line.split()
		self.btypes = [int(line[0]), int(line[1])]
		self.ndx = line[0]+'&'+line[1]
		self.k = float(line[2])
		self.b0 = float(line[3])
		father.add_connection(self.btypes[0], self.btypes[1])

class ff_angle():
	def __init__(self, line):
		line = line.split()
		self.center = int(line[1])
		i = int(line[0])
		j = int(line[2])
		if i>j: self.atypes = [j,i]
		else: self.atypes = [i,j]
		self.ndx = line[0]+'&'+line[2]
		self.k = float(line[3])
		self.a0 = float(line[4])

class ff_torsion():
	def __init__(self, line):
		line = line.split()
		self.ndx = ''
		self.ndx1 = []
		for i in range(4):
			ii = abs(int(line[i]))
			self.ndx1.append(ii)
		if self.ndx1[1]<self.ndx1[2]:
			self.ndx += '%5d'%self.ndx1[1]
			self.ndx += '%5d'%self.ndx1[2]
			self.ndx += '%5d'%self.ndx1[0]
			self.ndx += '%5d'%self.ndx1[3]
		else:
			self.ndx += '%5d'%self.ndx1[2]
			self.ndx += '%5d'%self.ndx1[1]
			self.ndx += '%5d'%self.ndx1[3]
			self.ndx += '%5d'%self.ndx1[0]
			self.ndx1.reverse()
		self.k = float(line[4])
		self.sign = float(line[5])
		self.period = float(line[6])

class ff_improper():
	def __init__(self, line):
		line = line.split()
		self.center = int(line[2])
		self.ipr_types = [int(line[0]),int(line[1]),int(line[3])]
		self.ndx = line[0] + '&' + line[1] + '&' + line[2]
		self.k = float(line[4])
		self.sign = float(line[5])
		self.period = float(line[6])

class opls_top():
	def __init__(self, Pname, Iname, suf=0):
		self.pdb_atoms = {}

		self.map = {}
		self.oldndx = {}
		self.atoms = []
		self.nneigh = []
		self.neighbors = {}

		self.nonbond_param = {}
		self.bond_param = {}
		self.angle_param = {}
		self.tor_param = {}
		self.impr_param = {}

		self.tor_ndx_list = []

		self.read_pdb(Pname)
		self.read_schrodinger(Iname, suf)
		self.find_14()
		pass

	def add_connection(self, i, j):
		if j in self.map[i]: return
		self.map[i].append(j)
		self.map[j].append(i)

	def read_pdb(self, Iname):
		Ifile = open(Iname)
		ndx = 1
		while 1:
			line = Ifile.readline()
			if line=='': break

			if line.find('ATOM')==0 or line.find('HETATM')==0:
				self.pdb_atoms[ndx] = pdb_atom(line, self)
				ndx += 1

	def read_schrodinger(self, Iname, suf):
		Ifile = open(Iname)
		while 1:
			line = Ifile.readline()
			if line=='': break

			if line.find('*')==0: continue

			if 1: #line.find('INH')==0:
				line = line.split()
				self.natoms = int(line[1])
				self.nbonds = int(line[2])
				self.nangles = int(line[3])
				self.ntemp1 = int(line[4])
				self.ntemp2 = int(line[5])

				for i in range(self.natoms): self.map[i+1] = []

				for i in range(self.natoms):
					line = Ifile.readline()
					line = line.split()
					self.atoms.append(top_atom(line, self, suf))
					self.oldndx[int(line[5])] = int(line[0])

				## Number of neighbors (1-2, 1-3 and 1-4):
				while 1:
					line = Ifile.readline()
					if line=='':
						raise Exception, 'Bad file!'
					line = line.split()
					for i in line: self.nneigh.append(int(i))
					if len(self.nneigh)>=self.natoms: break

				## Neighbors:
				for i in range(self.natoms):
					line = Ifile.readline()
					line = line.split()
					self.neighbors[i+1] = []
					for j in line: 
						self.neighbors[i+1].append(int(j))

				break

		## nonbond parameters:
		while 1:
			line = Ifile.readline()
			if line=='':
				raise Exception, 'Bad file, no NBON found'

			if line.find('NBON')==0:
				for i in range(self.natoms):
					line = Ifile.readline()
					self.nonbond_param[i+1] = ff_nonbond(line)
				break

		## bond parameters:
		while 1:
			line = Ifile.readline()
			if line=='':
				raise Exception, 'Bad file, no BOND found'

			if line.find('BOND')==0:
				for i in range(self.nbonds):
					line = Ifile.readline()
					tempbond = ff_bond(line, self)
					if tempbond.ndx in self.bond_param:
						self.bond_param[tempbond.ndx+'@'] = tempbond
					else:
						self.bond_param[tempbond.ndx] = tempbond
				break

		## angle parameters:
		## The middle atom is the vertex atom.
		while 1:
			line = Ifile.readline()
			if line=='':
				raise Exception, 'Bad file, no THET found'

			if line.find('THET')==0:
				for i in range(self.nangles):
					line = Ifile.readline()
					tempangle = ff_angle(line)
					if tempangle.center in self.angle_param:
						if tempangle.ndx in self.angle_param[tempangle.center]:
							self.angle_param[tempangle.center][tempangle.ndx+'@'] = tempangle
						else:
							self.angle_param[tempangle.center][tempangle.ndx] = tempangle
					else:
						self.angle_param[tempangle.center] = {tempangle.ndx: tempangle}

				break

		## torsion parameters:
		while 1:
			line = Ifile.readline()
			if line=='':
				raise Exception, 'Bad file, no PHI found'

			if line.find('PHI')==0:
				## proper torsion data:
				while 1:
					line = Ifile.readline()
					if line.find('IPHI')==0: break

					temptor = ff_torsion(line)
					if temptor.ndx in self.tor_param:
						self.tor_param[temptor.ndx] += [temptor]
						#self.tor_ndx_list.append(temptor.ndx+'@')
					else:
						self.tor_param[temptor.ndx] = [temptor]
						self.tor_ndx_list.append(temptor.ndx)
					#self.tor_param[temptor.ndx2] = temptor

				## improper torsion data:
				while 1:
					line = Ifile.readline()
					if line.find('END')==0: break

					tempimpr = ff_improper(line)
					self.impr_param[tempimpr.center] = [tempimpr]

				break
		self.tor_ndx_list.sort()

		Ifile.close()

	def find_14(self):
		pair_14 = []
		for i in range(self.natoms):
			for j in self.neighbors[i+1]:
				if j in self.map[i+1]: continue
				IsPass = False
				for k in self.map[i+1]:
					if j in self.map[k]:
						IsPass = True
						break
				if IsPass: continue
				if j>0: pair_14.append([i+1,j])
		self.pair_14 = pair_14

	def tors_fourier2RB0(self, V, sign, period):
		res = []
		F = [0.0, 0.0, 0.0, 0.0]
		p = int(period)
		F[p-1] = V * 4.184
		if p%2==0 and sign>0.0: raise Exception, 'Torsion params not consistent.'
		if p%2!=0 and sign<0.0: raise Exception, 'Torsion params not consistent.'
		c0 = F[1] + 0.5*(F[0]+F[2])
		c1 = 0.5*(-F[0]+3.*F[2])
		c2 = -F[1] + 4.*F[3]
		c3 = -2.*F[2]
		c4 = -4.*F[3]
		c5 = 0.0
		return [c0,c1,c2,c3,c4,c5]

	def tors_fourier2RB(self, fourier):
		nterms = len(fourier)
		F = [0.0, 0.0, 0.0, 0.0]
		for i in range(nterms):
			p = int(fourier[i].period)
			F[p-1] = fourier[i].k * 4.184
			if p%2==0 and fourier[i].sign>0.0: raise Exception, 'Torsion params not consistent.'
			if p%2!=0 and fourier[i].sign<0.0: raise Exception, 'Torsion params not consistent.'
		c0 = F[1] + 0.5*(F[0]+F[2])
		c1 = 0.5*(-F[0]+3.*F[2])
		c2 = -F[1] + 4.*F[3]
		c3 = -2.*F[2]
		c4 = -4.*F[3]
		c5 = 0.0
		return [c0,c1,c2,c3,c4,c5]

	def write_top(self, Oname0, IsOld=True, IsWriteHead=True):
		Oname = os.path.splitext(Oname0)[0]
		Ofile = open(Oname+'_nb.itp', 'w')

		##################
		## atomtypes file:
		if IsWriteHead:
			Ofile.write('#define _FF_OPLS\n#define _FF_OPLSAA\n\n')
			Ofile.write('[ defaults ]\n')
			Ofile.write('; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ\n')
			Ofile.write('1               3               yes             0.5     0.5\n\n')

		Ofile.write('[ atomtypes ]\n')
		Ofile.write(';name  bond_type    mass    charge   ptype          sigma      epsilon\n')
		for i in range(self.natoms):
			Ofile.write('%5s'%self.atoms[i].atype)
			Ofile.write('  %5s'%self.atoms[i].atype)
			Ofile.write('   0.00   0.00  A  ')
			sig = self.nonbond_param[i+1].sig * 0.1 # unit:nm
			eps = self.nonbond_param[i+1].eps * 4.184 # unit:kJ
			Ofile.write('%9.6e'%sig)
			Ofile.write('  %9.6e\n'%eps)
		Ofile.write('\n')
		Ofile.close()


		#################
		## molecule file:
		Ofile = open(Oname+'.top', 'w')
		Ofile.write('#include "%s_nb.itp"\n\n'%Oname)

		Ofile.write('[ moleculetype ]\n; Name         nrexcl\n')
		Ofile.write('solute       3\n\n')

		Ofile.write('[ atoms ]\n')
		Ofile.write(';   nr       type  resnr residue  atom   cgnr     charge       mass  typeB    chargeB\n')
		for i in range(self.natoms):
			Ofile.write('%6d '%(i+1))
			if IsOld: 
				ndx = self.oldndx[i+1]
				tempndx = i+1
			else:     
				ndx = i+1
				tempndx = self.atoms[ndx-1].old_ndx
			Ofile.write('%10s '%self.atoms[ndx-1].atype)
			Ofile.write('    1 ')
			Ofile.write('  LIG ')
			Ofile.write('%6s '%self.pdb_atoms[tempndx].name)
			Ofile.write('%6d '%(i+1))
			Ofile.write('%10.5f '%self.nonbond_param[ndx].q)
			Ofile.write(' %10.5f\n'%ElemMass[self.pdb_atoms[tempndx].elem])
		Ofile.write('\n')

		## bonds:
		## scale_desmond2gmx: a factor of 2.0 is needed for desmond to gromacs:
		scale_desmond2gmx = 2.0
		Ofile.write('[ bonds ]\n')
		Ofile.write(';  ai    aj funct  r  k\n')
		texts = []
		for pair in self.bond_param.keys():
			thistext = ''
			i0 = self.bond_param[pair].btypes[0]
			i1 = self.bond_param[pair].btypes[1]
			if IsOld:
				i0 = self.atoms[i0-1].old_ndx
				i1 = self.atoms[i1-1].old_ndx
			thistext += '%5s  %5s   1 '%(i0,i1)
			b0 = self.bond_param[pair].b0 * 0.1 # unit:nm
			k = self.bond_param[pair].k * 4.184 * 100.0 * scale_desmond2gmx # unit:kJ/nm^2
			thistext += '%9.5f '%b0
			thistext += '%9.1f\n'%k
			texts.append( thistext )
		texts.sort()
		for tt in texts: Ofile.write(tt)
		Ofile.write('\n')

		## pairs:
		Ofile.write('[ pairs ]\n;  ai    aj funct\n')
		texts = []
		for pair in self.pair_14:
			thistext = ''
			i0 = pair[0]
			i1 = pair[1]
			if IsOld:
				i0 = self.atoms[i0-1].old_ndx
				i1 = self.atoms[i1-1].old_ndx
			if i0>i1:
				tempi = i1
				i1 = i0
				i0 = tempi
			thistext += '%6d %6d     1\n'%(i0,i1)
			texts.append( thistext )
		texts.sort()
		for tt in texts: Ofile.write(tt)
		Ofile.write('\n')

		## angles:
		## scale_desmond2gmx: a factor of 2.0 is needed for desmond to gromacs:
		scale_desmond2gmx = 2.0
		Ofile.write('[ angles ]\n')
		Ofile.write(';  i    j    k  func       th0       cth\n')
		for key in self.angle_param.keys():
			texts = []
			for other in self.angle_param[key]:
				#other = other.strip('@')
				thistext = ''
				i0 = self.angle_param[key][other].atypes[0]
				i1 = key
				i2 = self.angle_param[key][other].atypes[1]
				if IsOld:
					i0 = self.atoms[i0-1].old_ndx
					i1 = self.atoms[i1-1].old_ndx
					i2 = self.atoms[i2-1].old_ndx
				if i0>i2:
					thistext += '%5s '%i2
					thistext += '%5s '%i1
					thistext += '%5s '%i0
				else:
					thistext += '%5s '%i0
					thistext += '%5s '%i1
					thistext += '%5s '%i2
				thistext += '    1 '
				thistext += '%9.3f '%self.angle_param[key][other].a0
				k = self.angle_param[key][other].k * 4.184 * scale_desmond2gmx #unit: kJ/rad^2
				thistext += '%9.3f\n'%k
				texts.append( thistext )
			texts.sort()
			for tt in texts: Ofile.write(tt)
		Ofile.write('\n')

		## dihedraltypes:
		## scale_desmond2gmx: a factor of 2.0 is needed for desmond to gromacs:
		scale_desmond2gmx = 2.0
		Ofile.write('[ dihedrals ]\n')
		Ofile.write(';  i    j    k    l   func     coefficients\n')
		texts = {}
		for key in self.tor_ndx_list: #self.tor_param.keys():
			thiskey = ''
			thistext = ''
			tempiis = []
			for i in range(4):
				ii = self.tor_param[key][0].ndx1[i]
				if IsOld: ii = self.atoms[ii-1].old_ndx
				tempiis.append(ii)
				thistext += '%5s '%ii
			if tempiis[1]<tempiis[2]:
				thiskey += '%5s '%tempiis[1]
				thiskey += '%5s '%tempiis[2]
				thiskey += '%5s '%tempiis[0]
				thiskey += '%5s '%tempiis[3]
			else:
				thiskey += '%5s '%tempiis[2]
				thiskey += '%5s '%tempiis[1]
				thiskey += '%5s '%tempiis[3]
				thiskey += '%5s '%tempiis[0]
			thistext += '    3 '
			#c = self.tors_fourier2RB(self.tor_param[key].k,
			#			self.tor_param[key].sign,
			#			self.tor_param[key].period)
			c = self.tors_fourier2RB(self.tor_param[key])
			for i in range(6): thistext += '%10.5f '%(c[i]*scale_desmond2gmx)
			thistext += '\n'
			n_at = key.count('@')
			for i in range(n_at): thiskey += '@'
			texts[thiskey] = thistext
		torkeys = texts.keys()
		torkeys.sort()
		for tt in torkeys: Ofile.write( texts[tt] )
		Ofile.write('\n')

		## improper:
		## scale_desmond2gmx: a factor of 2.0 is needed for desmond to gromacs:
		scale_desmond2gmx = 2.0
		Ofile.write('[ dihedrals ]\n')
		Ofile.write(';  i    j    k    l   func     coefficients\n')
		for key in self.impr_param:
			i0 = self.impr_param[key][0].ipr_types[0]
			i1 = self.impr_param[key][0].ipr_types[1]
			i2 = self.impr_param[key][0].center
			i3 = self.impr_param[key][0].ipr_types[2]
			if IsOld:
				i0 = self.atoms[i0-1].old_ndx
				i1 = self.atoms[i1-1].old_ndx
				i2 = self.atoms[i2-1].old_ndx
				i3 = self.atoms[i3-1].old_ndx
			Ofile.write('%5s '%i0)
			Ofile.write('%5s '%i1)
			Ofile.write('%5s '%i2)
			Ofile.write('%5s    3 '%i3)
			#c = self.tors_fourier2RB(self.impr_param[key].k,
			#			self.impr_param[key].sign,
			#			self.impr_param[key].period)
			c = self.tors_fourier2RB(self.impr_param[key])
			for i in range(6): Ofile.write('%10.5f '%(c[i]*scale_desmond2gmx))
			#Ofile.write('%10.1f '%self.impr_param[key].k)
			#Ofile.write('%15.5f '%self.impr_param[key].sign)
			#Ofile.write('%6.0f'%self.impr_param[key].period)
			Ofile.write('\n')
		Ofile.write('\n')

		## write system:
		Ofile.write('[ system ]\n')
		Ofile.write('ICE\n\n')
		Ofile.write('[ molecules ]\n')
		Ofile.write('; Compound        nmols\n')
		Ofile.write('solute         1\n')

		Ofile.close()

if __name__=='__main__':
	(options, args) = read_args()
	top = opls_top(options.inputname, options.topname, int(options.suffix))
	top.write_top(options.outputname)
