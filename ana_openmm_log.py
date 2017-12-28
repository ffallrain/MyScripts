#!/usr/bin/python
import sys,os
import matplotlib.pyplot as plt

if len(sys.argv) <= 3:
    print "Usage: $0 md.log N_AVERAGE figure_title"
    sys.exit()
else:
    infile = sys.argv[1]
    AVERAGE = int(sys.argv[2])
    title = sys.argv[3]

outdir = "OUT_FIG"
if not os.path.isdir(outdir):
    os.mkdir(outdir)

print ">>>>> Loading data.."
lines = open(infile).readlines()
first_line = lines.pop(0)

N = len(lines)

names = list()
for name in first_line[1:].split(','):
    names.append( name[1:-1].replace('/','\\') )

data = dict()
for name in names:
    data[name] = list()

for line in lines:
    numbers = line.split(',')
    for (name,number) in zip(names,numbers):
        data[name].append(float(number))

print "----- Deriving averaged data.."
avg_data = dict()
for name in names:
    avg_data[name] = list()
    for i in range(N):
        left = min(i,AVERAGE/2)
        right = min(N-i,AVERAGE/2)
        avg = sum( data[name][i-left:i+right] ) / (left+right)
        avg_data[name].append(avg)

name0 = names[0]
for name1 in names:
    print "----- Ploting: %s "%name1
    figname = "%s/%s.png"%(outdir,name1)
    plt.plot(data[name0],data[name1],color = 'grey',label = 'Instaneous' )
    plt.plot(data[name0],avg_data[name1],color = 'red',label = 'Average' )
    plt.xlabel(name0)
    plt.ylabel(name1)
    plt.legend(loc='best')
    plt.title(title)
    plt.savefig(figname)
    plt.cla()

print "----- All done. "


