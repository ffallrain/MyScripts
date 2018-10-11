#!/usr/bin/python
import sys,os

try:
    comment = sys.argv[1]
except:
    comment = 'Default'

os.system("git add --all . ")
os.system("git commit -m '%s'"%comment)
os.system("git push")
