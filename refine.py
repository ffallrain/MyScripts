#!/bin/python
import sys,os

infile = sys.argv[1]
n_output = int(sys.argv[2])

assert infile [-4:] == '.pdb'
FLAG_TMP = 'TMP_PY_REFINE_FLAG'
COMMAND_TMP = 'TMP_PY_REFINE_COMMAND'

flag = '''
-s %s 
-pep_refine           
-ex1 
-ex2aro 
-nstruct %d              
-lowres_preoptimize    
-flexpep_score_only    
'''

command = '''
#!/bin/bash
cd $RST_WORKDIR

[ -x $RST_BIN/FlexPepDocking.$RST_BINEXT ] || exit 1

$RST_BIN/FlexPepDocking.$RST_BINEXT @%s -database $RST_DATABASE -run:constant_seed -nodelay  2>&1 \
    > refinement.log

test "${PIPESTATUS[0]}" != '0' && exit 1 || true  # Check if the first executable in pipe line return error and exit with error code if so
'''

ofp=open(FLAG_TMP,"w")
ofp.write(flag%(infile,n_output))
ofp.close()
ofp=open(COMMAND_TMP,"w")
ofp.write(command%FLAG_TMP)
ofp.close()
os.system("bash %s"%COMMAND_TMP)
os.system("rm %s %s"%(FLAG_TMP,COMMAND_TMP))

