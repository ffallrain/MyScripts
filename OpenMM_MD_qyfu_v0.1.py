#!/usr/bin/python
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout


FLAG_POSRES_HEAVY = True
FLAG_MINIM = False
FLAG_MD = True

inpdb = sys.argv[1]

class global_variable():
    pdb = None
    system = None
    integrator = None
    forcefield = None
    simulation = None
G = global_variable()

########################################################
####                Input pdb                       ####
########################################################

G.pdb = PDBFile(inpdb)

########################################################
####                Intergrator                     ####
########################################################
if True:
    G.integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)


########################################################
####        System  and force field                 ####
########################################################
if True :
    #######  Force Field
    G.forcefield = ForceField('amoeba2013.xml')
    #######  System 
    G.system = G.forcefield.createSystem(G.pdb.topology, nonbondedMethod=PME, nonbondedCutoff=1*nanometer, constraints=HBonds)
    #######  Position Restraint
    if FLAG_POSRES_HEAVY :# restraint Extra force
        atoms = [ x for x in G.pdb.topology.atoms()]
        heavy_atom_list = [ x for x in range(len(atoms)) if atoms[x].residue.name not in ('HOH','SOL','WAT') and atoms[x].element.symbol!='H']
        restr_list = heavy_atom_list

        harmonic_force_str = '1000.0*( (x-x0)*(x-x0) + (y-y0)*(y-y0) + (z-z0)*(z-z0) )'
        restr_force = CustomExternalForce(harmonic_force_str)
        restr_force.addPerParticleParameter('x0')
        restr_force.addPerParticleParameter('y0')
        restr_force.addPerParticleParameter('z0')
        for i in restr_list:
            restr_force.addParticle(i,G.pdb.positions[i])
        G.system.addForce(restr_force)
        ## pressure coupling
        G.system.addForce(MonteCarloBarostat(1*bar, 300*kelvin))

########################################################
####             Simulation                         ####
########################################################
if True :
    G.simulation = Simulation(G.pdb.topology, G.system, G.integrator)
    G.simulation.context.setPositions(G.pdb.positions)
    if FLAG_MINIM :
        G.simulation.minimizeEnergy()
        positions = G.simulation.context.getState(getPositions=True).getPositions()
        PDBFile.writeFile(G.simulation.topology, positions, open('minimized.pdb', 'w')) 
    elif FLAG_MD :
        pdbreporter = PDBReporter('traj.pdb',10)
        statedatareporter = StateDataReporter('md.log',10,step=True, time=True, potentialEnergy=True, kineticEnergy=True, totalEnergy=True, temperature=True, volume=True, density=True, speed=True, separator=',', systemMass=None, totalSteps=None )
        G.simulation.reporters.append(pdbreporter)
        G.simulation.reporters.append(statedatareporter)
        G.simulation.step(20000)
        positions = G.simulation.context.getState(getPositions=True).getPositions()
        PDBFile.writeFile(G.simulation.topology, positions, open('finished.pdb', 'w')) 
        print('Done')
