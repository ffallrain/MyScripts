#!/bin/python
import sys,os

infile = sys.argv[1]
outfile = sys.argv[2]

assert infile [-4:] == '.pdb'
TMP_OUTPUT = infile[:-4]+'_0001.pdb'
FLAG_TMP = 'TMP_PY_PREPACK_FLAG'
COMMAND_TMP = 'TMP_PY_PREPACK_COMMAND'

prepack_flag = '''
-s %s
-ex1 
-ex2aro 
-flexpep_prepack            
-nstruct 1                   # create one pre-packed structure - this is the standard in production runs too
'''

command = '''
#!/bin/bash

cd $RST_WORKDIR

[ -x $RST_BIN/FlexPepDocking.$RST_BINEXT ] || exit 1

$RST_BIN/FlexPepDocking.$RST_BINEXT @%s -database $RST_DATABASE -run:constant_seed -nodelay  2>&1 \
    > prepack.log

test "${PIPESTATUS[0]}" != '0' && exit 1 || true  # Check if the first executable in pipe line return error and exit with error code if so
'''

ofp=open(FLAG_TMP,"w")
ofp.write(prepack_flag%infile)
ofp.close()
ofp=open(COMMAND_TMP,"w")
ofp.write(command%FLAG_TMP)
ofp.close()
os.system("bash %s"%COMMAND_TMP)
os.system("mv %s %s"%(TMP_OUTPUT,outfile))
os.system("rm %s %s"%(FLAG_TMP,COMMAND_TMP))


