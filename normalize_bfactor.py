#!/usr/bin/python
import math
import sys,os

infile  = sys.argv[1]
# chainID = sys.argv[2]
outfile = sys.argv[2]

s_bf = 0.
s_bf2 = 0.
n_atom = 0.
avg_bf = 0.
for line in open(infile):
    if len(line)<6 or line[0:6] not in ('ATOM  ','HETATM'):
        continue
#    if line[21]!=chainID:
#        continue
    n_atom += 1
    bf      = float(line[60:66])
    s_bf   += bf
    s_bf2  += bf*bf

print s_bf
print s_bf2
print n_atom
avg_bf = s_bf/n_atom
sd = math.sqrt( s_bf2/n_atom - avg_bf**2 )
print sd
print avg_bf

ofp = open(outfile,"w")
for line in open(infile):
    if len(line)<6 or line[0:6] not in ('ATOM  ','HETATM'):
        ofp.write(line)
        continue
#    if line[21]!=chainID:
#        ofp.write(line)
#        continue
    else:
        bf = float(line[60:66])
        new_bf = ( bf - avg_bf ) / sd 
        ofp.write("%s%6.2f%s"%(line[0:60],new_bf,line[66:]))
    pass

        

