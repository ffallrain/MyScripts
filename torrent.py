#!/usr/bin/python
import sys,os
initial = sys.argv[1] 
N_child = int(sys.argv[2])
N_cycle = int(sys.argv[3])

tmpfile = '__torrent_tmp_pdb.pdb'

os.system("prepack.py %s %s"%(initial,tmpfile)) 
os.system("mv %s %s"%(tmpfile,initial))
print ">>>>> Initial input structure :%s  prepacked"%initial

to_refine_list = [initial,]
for i in range(N_cycle): 
    tmp_list = []
    for item in to_refine_list:
        os.system("refine.py %s %d"%(item,N_child)) 
        for _ in range(N_child):
            tmp_list.append(item[:-4]+"_%04d.pdb"%(_+1))
        print ">>>>> Refined %s"%item
    to_refine_list = tmp_list

