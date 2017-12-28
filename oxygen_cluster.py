#!/usr/bin/python
import sys,os
import numpy as np
import math
import scipy.cluster.vq as vq
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import Birch
from sklearn.cluster import DBSCAN
from sklearn.cluster import MeanShift, estimate_bandwidth

DIST_CUTOFF = 2.0
# SHOW_CUTOFF = 50
N_CLUSTER = 100

######################################################
######            Usage 
######################################################
if True:
    infile = 'OCLUSTER.pdb'
    outfile = 'cluster.pdb'
    centerfile = 'SPA_oxygen_cluster.pdb'

######################################################
######            Load Data 
######################################################
if True:
    data = list()
    frame = list()
    pdb_lines = list()
    model_n = 0
    for line in open(infile):
        if 'ATOM  ' in line or 'HETATM' in line:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            data.append( np.array([x,y,z]) )
            frame.append(model_n)
            pdb_lines.append(line)
        elif 'ENDMDL' in line:
            model_n += 1
    data = np.array( data )
    frame = np.array( frame )
    LENGTH = len(data)

######################################################
######            Cluster 
######################################################
if True:
    if False:   ### DBSCAN, in this model N_CLUSTER is not used , N_GROUP is guessed
        db = DBSCAN(eps=1.0 , min_samples=None)
        db.fit(data)
        clu_group = db.labels_
        clu_dist = np.zeros( (len(data),)) # not finished
        
    if False: ## Birch method. slow if n_cluster is large
        bir = Birch(threshold=1.5, n_clusters=N_CLUSTER)
        bir.fit(data)
        clu_group = bir.labels_
        clu_dist = np.zeros( (len(data),)) # not finished

    if False:  # minibatch kmeans. (very fast batch kmeans)
        mbk = MiniBatchKMeans(init='k-means++', n_clusters=N_CLUSTER, batch_size=100,
                              n_init=10, max_no_improvement=10, verbose=0,
                              random_state=0)

        mbk.fit(data)
        mbk_means_labels_unique = np.unique(mbk.labels_)
        clu_group = mbk.labels_
        clu_centers = mbk.cluster_centers_

        # print 'clu_group',clu_group
        # print 'clu_center',clu_centers

    if False:  ## cluster.vq method  ( k-means )
        whitened = vq.whiten(data)
        code_book,n = vq.kmeans(data,N_CLUSTER)
        clustered = vq.vq(data,code_book)
        clu_group,clu_dist =clustered

    if True : ## shift means 
        bandwidth = estimate_bandwidth(data, quantile=0.3 )
        ms = MeanShift(bandwidth=1.5 , bin_seeding=True)
        ms.fit(data)
        clu_group = ms.labels_
        clu_centers = ms.cluster_centers_


######################################################
######    check cluster
######################################################
if True:
    groups = np.unique([x for x in clu_group if x>=0 ])
    frames_of_group = dict()
    for group in groups:
        frames_of_group[group] = [ frame[i] for i in range(LENGTH) if clu_group[i] == group ]

######################################################
######    OutPut PDB 
######################################################
if True: ### clustered oxygen
    ofp = open(outfile,'w')
    for group in groups:
        ofp.write("MODEL     %4d\n"%group)
        for i in range(LENGTH):
            data_point = data[i]
            x,y,z = data_point
            group_i = clu_group[i]
            if group_i == group:
                ofp.write(pdb_lines[i])
        ofp.write("ENDMDL\n")
    ofp.close()

if True: ### centroid
    ofp = open(centerfile,'w')
    for i in range(len(clu_centers)):
        x,y,z = clu_centers[i]
        ofp.write("ATOM  %5d  OW  SOL  %4d    %8.3f%8.3f%8.3f       1.000\n"%(i,i,x,y,z))
    ofp.close()
sys.exit()

#  ######################################################
#  ###### Calculate cluster center and distances
#  ######################################################
#  if True:
#      ### center
#      centers = dict()
#      for i in range(LENGTH):
#          group = clu_group[i]
#          if centers.has_key(group):
#              n = len(centers[group])
#              centers[group] = ( centers[group]*n + data[i] )/(n + 1)
#          else:
#              centers[group] = data[i]
#  
#      ### distances
#      clu_dist = list()
#      for i in range(LENGTH):
#          center = centers[clu_group[i]]
#          current_hbond = data[i] 
#          current_dist = math.sqrt( sum([ (center[i]-current_hbond[i])**2 for i in range(6) ]) )
#          clu_dist.append( current_dist )
#  
#  ######################################################
#  ######     filter out ophernized values
#  ######################################################
#  if True :
#      keep_hbonds = np.ones( (LENGTH,) )
#      for i in range(LENGTH):
#          if clu_dist[i] > DIST_CUTOFF:
#              keep_hbonds[i] = 0
#  
#  ######################################################
#  ###### Calculate group properties
#  ######################################################
#  if True:
#      groups = np.unique( [ x for x in clu_group if x>=0 ] )
#      # groups = np.unique(clu_group)
#      N_GROUPS = len(groups)
#      frames_of_group = dict()
#  
#      ###  hbonds
#      for group in groups:
#          frames_of_group[group] = [ frame[i] for i in range(LENGTH) if clu_group[i] == group and keep_hbonds[i] ]
#      ###  Occupy
#      occupy = dict()
#      for group in groups:
#          total_hbonds = len(frames_of_group[group])
#          total_frames = len(np.unique(frames_of_group[group]))
#          occupy[group] = total_frames
#      ###  Dispersion
#      dispersion = dict()
#      for group in groups:
#          frames = frames_of_group[group]
#          disp = math.sqrt( sum( [ clu_dist[i]**2 for i in frames ] )/(1e-5+occupy[group]) )
#          dispersion[group] = disp
#  
#      ### energy
#      avgenergy = dict()
#      tmp_n = dict()
#      for i in range(LENGTH):
#          current_group = clu_group[i]
#          current_e = energy[i]
#          if avgenergy.has_key(current_group):
#              avgenergy[current_group] = (tmp_n[current_group]*avgenergy[current_group] + current_e )/(tmp_n[current_group] + 1)
#              tmp_n[current_group] += 1
#          else:
#              avgenergy[current_group] = current_e
#              tmp_n[current_group] = 1
#  
#      ### group show cutoff
#      keep_groups = np.zeros( (N_GROUPS,) )
#      for group in groups:
#          if len(frames_of_group[group]) >= SHOW_CUTOFF:
#              keep_groups[group] = True
#              # print "Keep groups" , keep_groups
#  
#  ######################################################
#  ######    OUTPUT -  centers
#  ######################################################
#  if True:
#      ### Strings
#      head = '''@<TRIPOS>MOLECULE \n HBOND \n %d %d %d 0 0 \n SMALL \n NO_CHARGES \n \n \n'''
#      atom_head = '@<TRIPOS>ATOM\n'
#      bond_head = '@<TRIPOS>BOND\n'
#      donor_line = '%6d O        %12.4f  %12.4f  %12.4f N.3 %5d %5d %12.4f %12.4f\n'
#      acceptor_line = '%6d N        %12.4f  %12.4f  %12.4f O.3  %5d %5d %12.4f %12.4f\n'
#      bond_line = '%6d %6d %d 1  \n'
#      assert  len(groups) == len(occupy) == len(dispersion)
#  
#      ### ofp handle
#      ofp = open(centerfile,'w')
#  
#      ### head
#      n_kept_hbonds = sum(keep_groups)
#      ofp.write(head%(2*n_kept_hbonds,n_kept_hbonds,n_kept_hbonds))
#      ofp.write(atom_head)
#  
#      ### atoms
#      atom_index = 0
#      for i in range(len(groups)):
#          if keep_groups[i]:
#              atom_index += 2
#              n_atom = atom_index-1
#              n_res = i
#              coords_1 = centers[i][:3]
#              coords_2 = centers[i][3:]
#              group = occupy[i]
#              dist = dispersion[i]
#              e = avgenergy[i]
#              ofp.write(donor_line%(n_atom,coords_1[0],coords_1[1],coords_1[2],group,n_res,e,dist))
#              ofp.write(acceptor_line%(n_atom+1,coords_2[0],coords_2[1],coords_2[2],group,n_res,e,dist))
#          else:
#              pass
#  
#      ### bonds
#      ofp.write(bond_head)
#      bond_index = 0
#      for i in range(len(groups)):
#          if keep_groups[i]:
#              bond_index += 1
#              a = bond_index * 2 - 1
#              b = bond_index * 2 
#              ofp.write(bond_line%(bond_index,a,b))
#          else:
#              pass
#      ofp.close()
#  
#  ######################################################
#  ######    OUTPUT - all colored hbonds (mol2)
#  ######################################################
#  if True:
#      ### Strings
#      head = '''@<TRIPOS>MOLECULE \n tmp.pdb \n %d %d %d 0 0 \n SMALL \n NO_CHARGES \n \n \n'''
#      atom_head = '@<TRIPOS>ATOM\n'
#      bond_head = '@<TRIPOS>BOND\n'
#      donor_line = '%6d O        %12.4f  %12.4f  %12.4f N.3  %5d %5d %12.4f \n'
#      acceptor_line = '%6d N        %12.4f  %12.4f  %12.4f O.3  %5d %5d %12.4f \n'
#      bond_line = '%6d %6d %d 1  \n'
#      assert  len(clu_group) == len(clu_dist) == len(data)
#  
#      ### ofp handle
#      ofp = open(outfile,'w')
#  
#      ### head
#      n_kept_hbonds = sum( keep_hbonds )
#      ofp.write(head%(n_kept_hbonds,n_kept_hbonds/2,n_kept_hbonds/2))
#      ofp.write(atom_head)
#  
#      ### atoms
#      atom_index = 0
#      res_index = 0
#      for i in range(LENGTH):
#          if keep_hbonds[i]:
#              atom_index += 2
#              res_index += 1
#              n_atom = atom_index-1
#              n_res = res_index
#              coords_1 = data[i][:3]
#              coords_2 = data[i][3:]
#              group = clu_group[i]
#              dist = clu_dist[i]
#     #         e = avgenergy[i]
#              ofp.write(donor_line%(n_atom,coords_1[0],coords_1[1],coords_1[2],n_res,group,e))
#              ofp.write(acceptor_line%(n_atom+1,coords_2[0],coords_2[1],coords_2[2],n_res,group,e))
#          else: 
#              pass
#  
#      ### bonds
#      ofp.write(bond_head)
#      bond_index = 0
#      for i in range(LENGTH):
#          if keep_hbonds[i]:
#              bond_index += 1
#              a = bond_index * 2 - 1
#              b = bond_index * 2 
#              ofp.write(bond_line%(bond_index,a,b))
#          else: 
#              pass
#      ofp.close()
#  
#  ######################################################
#  ######    OUTPUT Hbonds exist time output
#  ######################################################
#  if True:
#      ofp = open(exist_time_file,'w')
#      for group in groups:
#          line = "%d "%group
#          for n in frames_of_group[group]:
#              line = line + "%d "%n
#          line = line + '\n'
#          ofp.write(line)
#      ofp.close()
#      
    
