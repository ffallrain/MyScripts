#!/usr/bin/python
import sys,os

usage = '''
$0  in.pdb emd.situs out.pdb [powell]
'''
if len( sys.argv ) <=3 :
    print usage
    sys.exit()
else:
    infile = sys.argv[1]
    mapfile = sys.argv[2]
    outfile = sys.argv[3]
if len(sys.argv)>4:
    powell = True
else:
    powell = False

colores = '~/Software/Situs/Situs_2.7.2/bin/colores'
situs_output_file = 'col_best_001.pdb'
if os.path.isfile(situs_output_file):
    print "!!!!! There is a %s file. This Script Will do nothing !"%situs_output_file
    print "!!!!! Exit with ERROR "
    sys.exit()
else:
    if powell:
        popt = ''
    else:
        popt = '-nopowell'
    os.system("%s %s %s %s"%(colores,mapfile,infile,popt))
    os.system("mv %s %s"%(situs_output_file,outfile))
    os.system("rm  col_best_*")
    os.system("rm col_hi_fil.sit  col_hi_fil.sit  col_lo_fil.sit  col_rotate.log  col_trans.log  col_trans.sit")

print 'Done'
    



