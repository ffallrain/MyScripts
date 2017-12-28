#!/usr/bin/python
import sys,os

pbcline = 'CRYST1 %12.6f %12.6f %12.6f  90.00  90.00  90.00 P 1           1\n'
modelline = 'MODEL%9d\n'
endmdlline = 'ENDMDL\n'
water3lines = '''ATOM  %5d  OW  SOL  %4d    %8.3f%8.3f%8.3f  1.00  0.00           O
ATOM  %5d  HW1 SOL  %4d    %8.3f%8.3f%8.3f  1.00  0.00           H
ATOM  %5d  HW2 SOL  %4d    %8.3f%8.3f%8.3f  1.00  0.00           H\n'''

infile = sys.argv[1]

ifp = open(infile)
ofp = open("%s.pdb"%infile,'w')
while True:
    line = ifp.readline()
    if line == '':
        break
    elif "TIMESTEP" in line:
        line = ifp.readline()
        index = int(line)
        ofp.write(modelline%index)
    elif "NUMBER OF ENTRIES" in line or "NUMBER OF ATOMS" in line:
        line = ifp.readline()
        num_water = int(line)/3
    elif "BOX BOUNDS" in line:
        tmp =  ifp.readline().split()
        x = float(tmp[1])
        xl = float(tmp[0])
        tmp =  ifp.readline().split() 
        y = float(tmp[1])
        yl = float(tmp[0])
        tmp =  ifp.readline().split() 
        z = float(tmp[1])
        zl = float(tmp[0])
        ofp.write(pbcline%(x-xl,y-yl,z-zl))
    elif "ITEM: ENTRIES" in line or "ATOMS id type x y z" in line:
        for i in range(num_water):
            x_line = ifp.readline()
            h_line = ifp.readline()
            H_line = ifp.readline()
            ox = float(x_line.split()[2])
            oy = float(x_line.split()[3])
            oz = float(x_line.split()[4])
            hx = float(h_line.split()[2])
            hy = float(h_line.split()[3])
            hz = float(h_line.split()[4])
            Hx = float(H_line.split()[2])
            Hy = float(H_line.split()[3])
            Hz = float(H_line.split()[4])
            ofp.write(water3lines%(3*i+1,i+1,ox,oy,oz,3*i+2,i+1,hx,hy,hz,3*i+3,i+1,Hx,Hy,Hz))
        ofp.write(endmdlline)
    else:
        pass
        
        
