#!/usr/bin/python
import sys,os


def next_family(ifp):
    family = None
    flag_head = True
    for line in ifp:
        if flag_head :
            if 'Family' in line:
                flag_head = False
                family = list()
                family.append(line)
        else:
            if 'Family' in line:
                yield family
                family = list()
                family.append(line)
            else :
                family.append(line)
    yield family

def get_id(family):
    line = family[1]
    name = line[46:56].strip()
    index = int(name[1:])
    return index

def write_family(ofp,family):
    for line in family:
        ofp.write(line)

# load db2 list
db2_list = list()
for line in open('db2_list'):
    db2_list.append( int(line) )


ifp = open('all.db')
ofp = open('tmp','w')
for family in next_family(ifp):
    if get_id(family) in db2_list:
        write_family(ofp,family)
ofp.close()
print 'Done'
        
    
