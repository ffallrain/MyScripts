#!/usr/bin/python
import sys,os


#######################################
#####     Function next_frame 
#####     Function write_frame
#######################################
def next_frame(ifp):
    frame = list()
    for line in ifp:
        if len(line.split()) == 1:
            if len(frame) != 0:
                yield frame
                frame = list()
                frame.append(line)
            else:
                frame = list()
                frame.append(line)
        else:
            frame.append(line)
    yield frame

def write_frame(ofp,frame,n_model):
    for line in frame:
        ofp.write(line)

#######################################
#####     Function wrap_frame 
#######################################
def is_atom(line):
    if len(line.split())<6:
        return False
    elif '.' in line.split()[0]:
        return False
    else:
        return True

def get_center(frame):
    left = [9999,9999,9999]
    right = [ -9999,-9999,-9999 ]
    for line in frame:
        if is_atom(line):
            atomtype = int(line.split()[5])
            if atomtype > 246:
                continue
            else:
                x = float(line.split()[2])
                y = float(line.split()[3])
                z = float(line.split()[4])
                coord = x,y,z
                for i in (0,1,2):
                    if coord[i] < left[i] :
                        left[i] = coord[i]
                    if right[i] < coord[i] :
                        right[i] = coord[i]
        else:
            pass
    center = [ 0.5*(left[i]+right[i]) for i in 0,1,2 ]
    return center

def get_abc(frame):
    ## tinker .xyz file
    pbcline = frame[1]
    items = pbcline.split()
    assert len(items) == 6
    x = float(items[0])
    y = float(items[1])
    z = float(items[2])
    return (x,y,z)

def wrap_atom(abc, center,coord ):
    new_coord = list(coord)
    for i in (0,1,2):
        if coord[i] - center[i] < -0.5*abc[i]:
            new_coord[i] = coord[i] + abc[i]
        if coord[i] - center[i] >  0.5*abc[i]:
            new_coord[i] = coord[i] - abc[i]
        else:
            pass
    return new_coord

def gen_line(line,new_coord):
    x,y,z = new_coord
    new_line = "%s%12.6f%12.6f%12.6f%s"%(line[:11],x,y,z,line[47:])
    return new_line

def wrap(frame,abc,center):
    new_frame = list()
    for line in frame:
        if is_atom(line):
            x = float(line.split()[2])
            y = float(line.split()[3])
            z = float(line.split()[4])
            coord = (x,y,z)
            new_coord = wrap_atom( abc,center,coord )
            new_line = gen_line(line,new_coord)
        else:
            new_line = line
        new_frame.append(new_line)
    return new_frame
   
def wrap_frame( frame ):
    abc = get_abc( frame )
    center = get_center(frame) # (x,y,z)
    new_frame = wrap( frame,abc,center )
    return new_frame

## Main
if True:
    infile = sys.argv[1]
    outfile = sys.argv[2]
    ifp = open(infile)
    ofp = open(outfile,'w')
    n_model = 0
    for frame in next_frame( ifp ):
        n_model += 1
        new_frame = wrap_frame(frame)
        write_frame( ofp, new_frame, n_model )
        print "Processed model %d"%n_model
    ifp.close()
    ofp.close()
    print "Done."
