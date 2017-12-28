#!/usr/bin/python
import sys,os

K = 40.
scale = 400.

winner = int(sys.argv[1])
loser = int(sys.argv[2])

Ew = 1.0/(1+10**( (loser-winner)/scale ) )
El = 1.0/(1+10**( (winner-loser)/scale ) )

difference = (1-Ew)*K
difference2 = ( 0-El)*K

print "Diff: %g"%difference
print "Diff2: %g"%difference2
print "New winner : %g"%(winner+difference)
print "New loser : %g"%(loser-difference)
