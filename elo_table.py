#!/usr/bin/python
import sys,os

K = 40.
scale = 400.

for diff in range(-500,500,20):
    Ew = 1.0/(1+10**( diff/scale ) )
    difference = (1-Ew)*K
    print "%d: %8.3f"%(diff,difference)
        
