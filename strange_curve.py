#!/usr/bin/python
import sys,os
import matplotlib.pyplot as plt
import math

step = 1e-6
D = 1

xt = 0.
yt = 0.


x = [xt,]
y = [yt,]

n = 0
while True:
    n += 1
    slope = (xt-yt)/(D-xt-yt)
    if D-xt-yt>0:
        angle = math.atan(slope)
    else:
        angle = math.pi + math.atan(slope)
    dx = step*math.cos(angle)
    dy = step*math.sin(angle) 
    xt = xt + dx
    yt = yt + dy
    x.append(xt)
    y.append(yt)
    if abs(xt-D/2.) < step and abs(yt-D/2.) < step:
        print n
        break

x2 = [ D-yt for yt in y ]
y2 = [ xt for xt in x ]

x3 = [ yt for yt in y ]
y3 = [ D-xt for xt in x]

x4 = [ D-xt for xt in x ]
y4 = [ D-yt for yt in y ]

data = ( (x,y),(x2,y2),(x3,y3),(x4,y4) )

plt.figure(figsize = (4,4) )
plt.plot(x,y,color = 'g', alpha=0.5,linewidth = 2)
plt.plot(x2,y2,color = 'r', alpha=0.5,linewidth = 2)
plt.plot(x3,y3,color = 'b', alpha=0.5,linewidth = 2)
plt.plot(x4,y4,color = 'y', alpha=0.5,linewidth = 2)
plt.title("Strange Curve")
plt.xlim( (0,D) )
plt.ylim( (0,D) )
plt.show()
    



