#!/usr/bin/python
import sys,os
import fpdb
import pickle 
import matplotlib.pyplot as plt

infile = sys.argv[1]
try:
    title = sys.argv[2]
except:
    title = "RMSF"

# load coords

if True:
    coords = list()
    f1 = next(fpdb.next_frame(infile))
    for line in f1: 
        if len(line) > 54 and line[17:20] in fpdb.standard_protein_residues:
            coords.append( list() )
            
    print len(coords)

    n_frame = 0
    for frame in fpdb.next_frame(infile):
        n = 0 
        for line in frame:
            if len(line) > 54 and line[17:20] in fpdb.standard_protein_residues:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                coords[n].append((x,y,z))
                n += 1
        n_frame += 1
        print n_frame
    pickle.dump(coords,open('coords.dump','w'))
else:
    coords = pickle.load(open('coords.dump'))
            

avg = list()
for coord in coords:
    s_x = sum( [ x[0] for x in coord ] )
    s_y = sum( [ x[1] for x in coord ] )
    s_z = sum( [ x[2] for x in coord ] )
    a_x = s_x / len(coord)
    a_y = s_y / len(coord)
    a_z = s_z / len(coord)
    
    avg.append( (a_x,a_y,a_z) )

pickle.dump(avg,open('avg.dump','w'))

rmsf = list()
for coord,a in zip(coords,avg):
    s = sum( [ fpdb.dist(x,a) for x in coord ] )
    rmsf.append( (s/len(coord))**0.5 ) 

plt.plot(rmsf)
plt.xlabel("Atom Index")
plt.ylabel("RMSF ( Angstram )")
plt.title(title)
plt.savefig("rmsf.png")

plt.show()
    
