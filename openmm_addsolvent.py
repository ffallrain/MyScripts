#!/usr/bin/python
from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout

class files():
    inpdb = sys.argv[1]
    minimize = 'minimize_addsolvent.pdb'
    traj = 'traj.pdb'
    mdlog = 'md.log'
    lastframe = 'finished.pdb'
    restart = 'checkpoint.restart'
    error = 'error_save.pdb'
F = files()

class parameters():
    box_buffer = 1.0*nanometer # when there is no box information in PDB file, the script will generate one ,here the buffer size 
    nsteps = 500 * 1000 
    stepsize = 0.002*picoseconds
    nsavetraj = 100
    ndatareprot = 100
    T = 300*kelvin
    P = 1*bar
    forcefield = 'amber99sb.xml' #'amber99sb.xml'
    watermodel = 'tip3p.xml' #None #'tip3p.xml'
    nonbondedMethod = PME
    nonbondedCutoff = 1*nanometer 
    constraints = HBonds
    rigidWater = True
    removeCMMotion = True
    frictionCoeff = 1/picosecond
    platform = 'CUDA'
    FLAG_PRESSURE_COUPLING = True
    FLAG_POSRES_HEAVY = True
    FLAG_MINIM = True
    FLAG_MD = False
    FLAG_ADDSOLVENT = True
P = parameters()

class global_variable():
    pdb = None
    system = None
    integrator = None
    forcefield = None
    simulation = None
    modeller = None
G = global_variable()

########################################################
####                Input pdb                       ####
########################################################

G.pdb = PDBFile(F.inpdb)
###### If pdb file do not contain a vector of box parameters
if G.pdb.topology.getUnitCellDimensions() == None:
    xmin = min([x[0] for x in G.pdb.positions])
    xmax = max([x[0] for x in G.pdb.positions])
    ymin = min([x[1] for x in G.pdb.positions])
    ymax = max([x[1] for x in G.pdb.positions])
    zmin = min([x[2] for x in G.pdb.positions])
    zmax = max([x[2] for x in G.pdb.positions])
    a = xmax - xmin + 2 * P.box_buffer
    b = ymax - ymin + 2 * P.box_buffer
    c = zmax - zmin + 2 * P.box_buffer
    dimension = Quantity( (a,b,c) )
    G.pdb.topology.setUnitCellDimensions( dimension )
else:
    pass

########################################################
####                Intergrator                     ####
########################################################
if True:
    G.integrator = LangevinIntegrator(P.T, P.frictionCoeff, P.stepsize)


########################################################
####              Force Field                       ####
########################################################
if True:
    if P.watermodel != None:
        G.forcefield = ForceField(P.forcefield,P.watermodel)
    else:
        G.forcefield = ForceField(P.forcefield)

########################################################
####                Add solvent                     ####
########################################################
if P.FLAG_ADDSOLVENT:
    G.modeller = Modeller(G.pdb.topology, G.pdb.positions)
    G.modeller.addSolvent(G.forcefield)

########################################################
####              System                            ####
########################################################
if True:
    #######  
        
    G.system = G.forcefield.createSystem(G.modeller.topology, 
                                         nonbondedMethod = P.nonbondedMethod, 
                                         nonbondedCutoff = P.nonbondedCutoff, 
                                         constraints     = P.constraints, 
                                         rigidWater      = P.rigidWater ,
                                         removeCMMotion  = P.removeCMMotion )

    #######  Position Restraint
    if P.FLAG_POSRES_HEAVY :
        harmonic_force_str = '1000.0*( (x-x0)*(x-x0) + (y-y0)*(y-y0) + (z-z0)*(z-z0) )'
        restr_force = CustomExternalForce(harmonic_force_str)
        restr_force.addPerParticleParameter('x0')
        restr_force.addPerParticleParameter('y0')
        restr_force.addPerParticleParameter('z0')

        atoms = G.modeller.topology.atoms()
        restr_list = [ x.index for x in atoms 
                       if x.residue.name not in ('HOH','SOL','WAT')
                          and  x.element.symbol!='H' ]
        for i in restr_list:
            restr_force.addParticle(i,G.modeller.positions[i])
        G.system.addForce(restr_force)
    
    #######  pressure coupling
    if P.FLAG_PRESSURE_COUPLING :
        G.system.addForce(MonteCarloBarostat(P.P, P.T))

########################################################
####             Simulation                         ####
########################################################
if True :
    platform = Platform.getPlatformByName(P.platform)
    G.simulation = Simulation(G.modeller.topology, G.system, G.integrator, platform)
    G.simulation.context.setPositions(G.modeller.positions)

    #######  Minimization
    if P.FLAG_MINIM :
        G.simulation.minimizeEnergy()
        positions = G.simulation.context.getState(getPositions=True).getPositions()
        PDBFile.writeFile(G.simulation.topology, positions, open(F.minimize, 'w')) 

    #######  Molecular dynamics
    elif P.FLAG_MD :
        pdbreporter = PDBReporter(F.traj,P.nsavetraj)
        G.simulation.reporters.append(pdbreporter)
        statedatareporter = StateDataReporter(F.mdlog, P.ndatareprot,  step=True, time       =True, potentialEnergy=True,
                                                    kineticEnergy=True, totalEnergy=True, temperature    =True, 
                                                           volume=True, density    =True, speed          =True, 
                                                        separator= ',', systemMass =None, totalSteps     =None )
        G.simulation.reporters.append(statedatareporter)
        try:
            G.simulation.step(P.nsteps)
        except:
            f = open(F.restart,'w')
            f.write(G.simulation.context.createCheckpoint())
            positions = G.simulation.context.getState(getPositions=True).getPositions()
            PDBFile.writeFile(G.simulation.topology, positions, open(F.error, 'w')) 
        positions = G.simulation.context.getState(getPositions=True).getPositions()
        PDBFile.writeFile(G.simulation.topology, positions, open(F.lastframe, 'w')) 
        print('Done')
