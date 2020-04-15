#!/usr/bin/env python
import sys,os
import argparse

parser = argparse.ArgumentParser('Compare two list')
parser.add_argument('files',type=str,nargs=2)

args = parser.parse_args()

filea,fileb = args.files

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
only_a = 0
only_b = 0
both = 0
for i in All:
    if i in a and i in b:
        both += 1
    elif i in a and i not in b:
        only_a += 1
    elif i not in a and i in b:
        only_b += 1

print(">>>>> Both: %d"%both)
print(">>>>> Only in %s: %d"%(filea,only_a))
print(">>>>> Only in %s: %d"%(fileb,only_b))


