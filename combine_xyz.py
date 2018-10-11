#!/usr/bin/python
import sys,os

infile1 = sys.argv[1]
infile2 = sys.argv[2]
outfile = sys.argv[3]

os.system("cp %s ./TMP_XYZ1.xyz"%infile1)
os.system("cp %s ./TMP_XYZ2.xyz"%infile2)
os.system("rm ./TMP_XYZ1.xyz_*")

os.system("echo TMP_XYZ1.xyz > TMP.INPUT")
os.system("echo 19 >> TMP.INPUT")
os.system("echo TMP_XYZ2.xyz >> TMP.INPUT")
os.system("echo  >> TMP.INPUT")

os.system("xyzedit.x < TMP.INPUT")
os.system("cp ./TMP_XYZ1.xyz_2 %s"%outfile)

os.system("rm TMP_XYZ* TMP.INPUT")

