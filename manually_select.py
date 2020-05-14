#!/usr/bin/env python
import sys,os
import argparse

parser = argparse.ArgumentParser( description="Manually pick items")
parser.add_argument("-i", help="Input item list file",type=str,required=True,)
parser.add_argument("-c", help="Command to run. ",type=str,required=True,)
parser.add_argument("-o", help="Output prefix, default is 'manually'.",type=str,default = "manually")


args = parser.parse_args()

positive_path = "%s_positive.list"%args.o
negative_path = "%s_negative.list"%args.o
listfile = args.i
prog = args.c

ofpp = open(positive_path,'w')
ofpn = open(negative_path,'w')

print(">>>>> Start selection ...")
for line in open(listfile):
    item = line.strip()
    print("     > Identifying %s"%line)
    os.system("%s %s"%(args.c,item))
    answer = input("     Keep? (Y/N,default N):")
    if len(answer.strip().lower()) > 0 and answer.strip().lower()[0] == 'y' :
        print("     + Keep %s"%item)
        ofpp.write("%s\n"%item)
    else:
        print("     + Ignore %s"%item)
        ofpn.write("%s\n"%item)

ofpp.close()
ofpn.close()


