#!/usr/bin/env python
import sys,os
import argparse

parser = argparse.ArgumentParser('Compare two list')
parser.add_argument('files',type=str,nargs=2)
parser.add_argument('-o',dest='o',action='store_true')

args = parser.parse_args()
filea,fileb = args.files
output_flag = args.o

# load a list()
a = list()
for line in open(filea):
    a.append(line.strip())


# load b list()
b = list()
for line in open(fileb):
    b.append(line.strip())

# create all
All = list()
for i in a :
    if i not in All:
        All.append(i)
for i in b :
    if i not in All:
        All.append(i)

# count
only_a = list()
only_b = list()
both = list()
for i in All:
    if i in a and i in b:
        both.append(i)
    elif i in a and i not in b:
        only_a.append(i)
    elif i not in a and i in b:
        only_b.append(i)

print(">>>>> Both: %d"%len(both))
print(">>>>> Only in %s: %d"%(filea,len(only_a)))
print(">>>>> Only in %s: %d"%(fileb,len(only_b)))

if output_flag:
    with open("Only_in_%s.list"%'a','w') as ofp:
        for i in only_a:
            ofp.write(i)
            ofp.write("\n")
    with open("Only_in_%s.list"%'b','w') as ofp:
        for i in only_b:
            ofp.write(i)
            ofp.write("\n")

        

