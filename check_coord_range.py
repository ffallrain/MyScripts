#!/usr/bin/python 
import sys,os
import matplotlib.pyplot as plt

infile = sys.argv[1]

x = list()
y = list()
z = list()

for line in open(infile):
    if "ATOM" in line or "HETATM" in line:
        x.append( float(line[30:38]) )
        y.append( float(line[38:46]) )
        z.append( float(line[46:54]) )

plt.figure(figsize=(12,4))
axx = plt.subplot(131)
axy = plt.subplot(132)
axz = plt.subplot(133)

axx.plot(x,color = 'green',alpha = 0.5,label='X')
axy.plot(y,color = 'green',alpha = 0.5,label='Y')
axz.plot(z,color = 'green',alpha = 0.5,label='Z')

plt.show()
