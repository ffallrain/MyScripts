#!/usr/bin/python
import sys,os

bf_flag = False
occ_flag = False
if sys.argv[1] == 'b':
    bf_flag = True
elif sys.argv[1] == 'o':
    occ_flag = True
else:
    raise StandardError

less_flag = False
larger_flag = False
express = sys.argv[2]
if express[0] == '+':
    larger_flag = True
elif express[0] == '-' or express[0].isdigit():
    less_flag = True
else:
    raise StandardError
cutoff = float(express[1:])

for line in sys.stdin:
    if len(line)<6 or line[0:6] not in ('HETATM','ATOM  '):
        continue
    if line[17:20] not in ('HOH','SOL','WAT'):
        continue
    else:
        if bf_flag:
            bf = float(line[60:66])
            num = bf
        elif occ_flag:
            occ = float(line[56:60])
            num = occ
        if less_flag and num <= cutoff:
            print line,
        if larger_flag and num >= cutoff:
            print line,
        pass
    pass
pass

