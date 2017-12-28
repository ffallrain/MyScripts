#!/usr/bin/python
import sys,os

infile = sys.argv[1]

MASS_O = 15.9994
MASS_H = 1.0079 
WATER_MASS = MASS_O + 2*MASS_H

def next_water(infile):
    current = list()
    for line in open(infile):
        if "OW" in line:
            current = [line,]
        elif "HW1" in line:
            current.append(line)
        elif "HW2" in line:
            current.append(line)
            yield current

if True: # load water paramters
    mess_centers = list()
    rela_os = list()
    rela_h1 = list()
    rela_h2 = list()
    inertia = list()
    for water in next_water(infile):

        ox = float(water[0].split()[3]) * 10  
        oy = float(water[0].split()[4]) * 10 
        oz = float(water[0].split()[5]) * 10 
        h1x = float(water[1].split()[3])* 10 
        h1y = float(water[1].split()[4])* 10 
        h1z = float(water[1].split()[5])* 10 
        h2x = float(water[2].split()[3])* 10 
        h2y = float(water[2].split()[4])* 10 
        h2z = float(water[2].split()[5])* 10  

        center_x = ( MASS_O*ox + MASS_H*h1x + MASS_H*h2x ) / (WATER_MASS)
        center_y = ( MASS_O*oy + MASS_H*h1y + MASS_H*h2y ) / (WATER_MASS)
        center_z = ( MASS_O*oz + MASS_H*h1z + MASS_H*h2z ) / (WATER_MASS)
        mess_centers.append( (center_x,center_y,center_z) )
        rela_ox = ox - center_x
        rela_oy = oy - center_y
        rela_oz = oz - center_z
        rela_os.append( (rela_ox,rela_oy,rela_oz) )
        rela_h1x = h1x - center_x
        rela_h1y = h1y - center_y
        rela_h1z = h1z - center_z
        rela_h1.append( (rela_h1x,rela_h1y,rela_h1z) )
        rela_h2x = h2x - center_x
        rela_h2y = h2y - center_y
        rela_h2z = h2z - center_z
        rela_h2.append( (rela_h2x,rela_h2y,rela_h2z) )
        
        ixx = ( rela_oy**2 + rela_oz**2 )*MASS_O + ( rela_h1y**2 + rela_h1z**2 )*MASS_H + ( rela_h2y**2 + rela_h2z**2 )*MASS_H
        iyy = ( rela_ox**2 + rela_oz**2 )*MASS_O + ( rela_h1x**2 + rela_h1z**2 )*MASS_H + ( rela_h2x**2 + rela_h2z**2 )*MASS_H
        izz = ( rela_oy**2 + rela_ox**2 )*MASS_O + ( rela_h1y**2 + rela_h1x**2 )*MASS_H + ( rela_h2y**2 + rela_h2x**2 )*MASS_H
        ixy = 0 - (rela_ox*rela_oy*MASS_O + rela_h1x*rela_h1y*MASS_H + rela_h2x*rela_h2y*MASS_H )
        iyz = 0 - (rela_oz*rela_oy*MASS_O + rela_h1z*rela_h1y*MASS_H + rela_h2z*rela_h2y*MASS_H )
        ixz = 0 - (rela_ox*rela_oz*MASS_O + rela_h1x*rela_h1z*MASS_H + rela_h2x*rela_h2z*MASS_H )
        inertia.append( (ixx,iyy,izz,ixy,ixz,iyz) )

if True: # Formatted Output
    print "Header"
    print "%d atoms"%216
    print "%d bodies"%216
    print "%d atom types"%3
    print "%g %g xlo xhi"%(0,18.6206)
    print "%g %g ylo yhi"%(0,18.6206)
    print "%g %g zlo zhi"%(0,18.6206)
    print 
    print "Atoms"
    print 

    for i in range(len(mess_centers)):
        x,y,z = mess_centers[i]
        print "%d %d %d %g %g %g %g 0 0 0 "%(i+1,1,1,WATER_MASS,x,y,z)

    print 
    print "Bodies"
    print
    for i in range(len(rela_os)):
        ox,oy,oz = rela_os[i]
        h1x,h1y,h1z = rela_h1[i]
        h2x,h2y,h2z = rela_h2[i]
        ixx,iyy,izz,ixy,ixz,iyz = inertia[i]
        print "%d %d %d"%(i+1,1,3*3+6)
        print "%d"%3
        print "%g %g %g %g %g %g"%(ixx,iyy,izz,ixy,ixz,iyz)
        print "%g %g %g"%(ox,oy,oz)
        print "%g %g %g"%(h1x,h1y,h1z)
        print "%g %g %g"%(h2x,h2y,h2z)
