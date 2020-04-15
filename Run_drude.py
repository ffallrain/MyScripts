#!/usr/bin/env python
from __future__ import print_function
from simtk.openmm import app
from simtk.openmm.app import PDBFile
from simtk.openmm.app import forcefield as ff
from simtk import openmm as mm
from simtk.unit import *
from sys import stdout, exit, stderr


from mdtraj import reporters as mdtj
from mdtraj.reporters import DCDReporter


import os 
import shutil
import numpy as np
import argparse


parser = argparse.ArgumentParser(description='Parameter For OpenMM')
parser.add_argument('-chfpre','--chfpre', help="CHARMM FileName's Prefix")
parser.add_argument('-jobname','--jobname', help="CHARMM FileName's Prefix")
parser.add_argument('-ftype','--ftype', help="Used Force Filed, C36 (Charmm36) or drude (Drude)")
parser.add_argument('-start','--start', type=int, help="Beginning Number of the job")
parser.add_argument('-end','--end', type=int, help="Ending Number of the job")

parser.add_argument('-nstep','--nstep',default=2500000, type=int, help="Step Number in Every Run")
parser.add_argument('-dumpint','--dumpint',default=50000, type=int, help="Step Number in Every Run")
parser.add_argument('-prePath','--prePath', default='./',help="Path for Output")
parser.add_argument('-box','--box', help="Box size x. Unit: angstrom")
parser.add_argument('-r','--restraint-heavy',dest='r',help="Restraint on heavy atoms. Yes or No(default)",default = 'No')
parser.add_argument('-rf','--restraint-force',dest='rf',help="Restraint force on heavy atoms.( Unit: J/nm2 )",default = 1000, type=int)


# Parameter Setting

args = parser.parse_args()

chfpre=args.chfpre
ftype=args.ftype.lower()
jobname=args.jobname+'-'+ftype

start=args.start
end=args.end
prePath=args.prePath
latt = args.box
restraint = args.r
restraint_force = args.rf

if not os.path.exists(prePath):
    os.makedirs(prePath)

latta = 86 * angstrom
lattb = 86 * angstrom
lattc = 86 * angstrom

box1=np.array([latta,0.00,0.00])
box2=np.array([0.00,lattb,0.00])
box3=np.array([0.00,0.00,lattc])

temp=298.15

if ftype == 'drude':
    dtemp=1.0
    timestep=0.001
    paralib='/pubhome/qyfu02/lck_drude/run1/drude_toppar_2018_10/'

if ftype == 'c36':
    timestep=0.002
    paralib='/home/qiuzy/paralib/charmm/toppar_c36_jul17/'

# Read PSF File

psf = app.CharmmPsfFile(chfpre+'.psf')
psf.setBox(latta,lattb,lattc,90.00*degree,90.00*degree,90.00*degree)
# crd = app.CharmmCrdFile(chfpre+'.crd')
crd = PDBFile(chfpre+'.pdb')


# Load the parameter set.
if ftype == 'drude':
    params = app.CharmmParameterSet(paralib+'toppar_drude_master_protein_2013f.str')
if ftype == 'c36':
    params = app.CharmmParameterSet(paralib+'top_all36_prot.rtf', paralib+'par_all36_prot.prm',paralib+'toppar_water_ions.str')


# Instantiate the system
platform=mm.Platform.getPlatformByName('CUDA')

if ftype == 'drude':
    system = psf.createSystem(params, nonbondedMethod=ff.PME, nonbondedCutoff=1.20, switchDistance=1.00, ewaldErrorTolerance=0.0001, constraints=ff.HBonds)
if ftype == 'c36':
    system = psf.createSystem(params, nonbondedMethod=ff.PME, nonbondedCutoff=1.20, switchDistance=1.00, ewaldErrorTolerance=0.0001, constraints=ff.HBonds)


system.addForce(mm.MonteCarloAnisotropicBarostat((1,1,1)*bar, temp*kelvin, True, True, True))

#if P.FLAG_POSRES_HEAVY :
if  restraint == 'Yes' :
    harmonic_force_str = '%f*( (x-x0)*(x-x0) + (y-y0)*(y-y0) + (z-z0)*(z-z0) )'%restraint_force
    restr_force = mm.CustomExternalForce(harmonic_force_str)
    restr_force.addPerParticleParameter('x0')
    restr_force.addPerParticleParameter('y0')
    restr_force.addPerParticleParameter('z0')

    atoms = crd.topology.atoms()

    restr_list = list()
    for x in atoms:
        if x.element != None:
            if x.residue.name not in ("HOH","SOL","WAT","SWM4","SWM6","SWM","POT"):
                if x.element.symbol != "D" :
                    # print(x.name,x.index,x.id,x.residue,x.element.symbol,x.element.name,x.element.mass)
                    restr_list.append(x.index)

    for i in restr_list:
        restr_force.addParticle(i,crd.positions[i])
    system.addForce(restr_force)


if ftype == 'drude':
    integrator = mm.DrudeLangevinIntegrator(temp*kelvin, 5/picosecond, dtemp*kelvin, 20/picosecond, timestep*picoseconds)
    integrator.setMaxDrudeDistance(0.25*angstrom)
if ftype == 'c36':
    integrator = mm.LangevinIntegrator(temp*kelvin, 1/picosecond, timestep*picoseconds)


simulation = app.Simulation(psf.topology, system, integrator, platform)
simulation.context.setPositions(crd.positions)

if ftype == 'drude':
    simulation.context.computeVirtualSites()


if start == 0:
    print(">>>>> Start minimization.")
    simulation.minimizeEnergy()
    print(">>>>> End minimization.")



#  Begin MD Simulation and Output Setting
if start == 0:
    simulation.context.setVelocitiesToTemperature(temp*kelvin)
else:
    if os.path.exists('chkrestart-'+jobname+'-'+str(start-1)+'.chk'):
        simulation.loadCheckpoint('chkrestart-'+jobname+'-'+str(start-1)+'.chk')
    elif os.path.exists('rstrestart-'+jobname+'-'+str(start-1)+'.rst'):
        with open('rstrestart-'+jobname+'-'+str(start-1)+'.rst', 'r') as f:
            simulation.context.setState(mm.XmlSerializer.deserialize(f.read()))
    else:
        raise 'NO File For Restart'


if start == 1:
    simulation.context.setPeriodicBoxVectors(box1,box2,box3)


nstep=args.nstep
dumpint=args.dumpint
logint=100

for i in range(start,end):
    print(">>>>> Simulation %d."%i)
    dcdf1='traj-'+jobname+'-'+str(i)+'.dcd'
    # dcdf2='traj-'+jobname+'-'+'lk'+'-'+str(i)+'.dcd'
    therf='ther-'+jobname+'-'+str(i)
    chkf='chkrestart-'+jobname+'-'+str(i)+'.chk'
    rstf='rstrestart-'+jobname+'-'+str(i)+'.rst'

    simulation.reporters.append(app.StateDataReporter(prePath+therf, logint, step=True, totalEnergy=True,\
                       potentialEnergy=True, kineticEnergy=True, temperature=True, volume=True, separator='     '))

    mdtjf1=prePath+dcdf1
    dcd1=mdtj.DCDReporter(mdtjf1,dumpint)
    simulation.reporters.append(dcd1)

    simulation.step(nstep)
    simulation.reporters.pop()
    dcd1.close()

    simulation.saveCheckpoint(prePath+chkf)


    state=simulation.context.getState(getPositions=True, getVelocities=True)

    with open(prePath+rstf, 'w') as f:
        f.write(mm.XmlSerializer.serialize(state))

    shutil.move(prePath+dcdf1,'./'+dcdf1) 
    shutil.move(prePath+therf,'./'+therf)
    shutil.move(prePath+chkf,'./'+chkf)
    shutil.move(prePath+rstf,'./'+rstf)
    
    print  (str(state.getPeriodicBoxVectors()))

