#!/usr/bin/python
import sys,os
import numpy as np 
import pickle

infile = sys.argv[1]
outfile = sys.argv[2]
resolution = 2.
bin_size = 0.5


grid_data = pickle.load(open(infile))
grid_shape = grid_data.shape
A,B,C = grid_shape

an, amin, amax = A,0,A-1
bn, bmin, bmax = B,0,B-1
cn, cmin, cmax = C,0,C-1

lattice_a = A*bin_size
lattice_b = B*bin_size
lattice_c = C*bin_size
lattice_alpha = 90.0
lattice_beta = 90.0
lattice_gamma = 90.0

comment_length = 1

ofp = open(outfile,'w')
#### Head
ofp.write("\n")
ofp.write("%8d\n"%comment_length)
for i in range(comment_length):
    ofp.write("REMARK   \n")
ofp.write("%8d%8d%8d"%(an,amin,amax))
ofp.write("%8d%8d%8d"%(bn,bmin,bmax))
ofp.write("%8d%8d%8d"%(cn,cmin,cmax))
ofp.write("\n")
ofp.write(" %8.5E %8.5E %8.5E"%(lattice_a,lattice_b,lattice_c))
ofp.write(" %8.5E %8.5E %8.5E"%(lattice_alpha,lattice_beta,lattice_gamma))
ofp.write("\n")
ofp.write("ZYX\n")

#### Body
for i in range(cn):
    ofp.write("%8d\n"%(i+cmin))
    s = grid_data[::,::,i].flatten()
    tmp_i = 0
    for num in s :
        ofp.write( "%12.5E"%num )
        tmp_i += 1 
        if tmp_i % 6 == 0 :
            ofp.write("\n")
    if tmp_i % 6 != 0 :
            ofp.write("\n")

#### Tail
ofp.write("%8d\n"%-9999)
ofp.write("  0.0000E+00   0.1000E+01\n")
ofp.close()
print "Done."
        
    

