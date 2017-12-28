#!/usr/bin/python
import sys,os
import matplotlib.pyplot as plt

infile = 'test.log'

class Value():
    def __init__(self,value,unit,interval = 0.):
        self.unit = unit
        self.interval = interval
        self.value = float(value)

class Point:
    def __init__(self,lines):
        assert len(lines) > 0 
        first_line = lines[0]
        value_lines = lines[1:]
        self.values = dict()
        if 'Average' in first_line:
            self.dynamic_step = int(first_line.split()[8])
            self.count = int(first_line.split()[5])
            self.type = 'avg'
        elif 'Instantaneous' in first_line:
            self.dynamic_step = int(first_line.split()[6])
            self.count = 1
            self.type = 'ins'
        else:
            self.type = None
            self.dynamic_step = 1
            self.count = 0
            print "##### WARNING %s"%first_line
            for line in value_lines:
                print line,
        
        for line in value_lines:
            if 'Simulation Time' in line:
                value = float(line.split()[2])
                unit  = line.split()[-1]
                # self.values['Simulation Time'] = Value(value,unit)
                self.values['Simulation Time'] = Value(value,unit)
            elif 'Total Energy' in line:
                value = float(line.split()[2])
                unit  = line.split()[3]
                interval = float(line[53:62])
                self.values['Total Energy'] = Value(value,unit,interval)
            elif 'Potential Energy' in line:
                value = float(line.split()[2])
                unit  = line.split()[3]
                interval = float(line[53:62])
                self.values['Potential Energy'] = Value(value,unit,interval)
            elif 'Kinetic Energy' in line:
                value = float(line.split()[2])
                unit  = line.split()[3]
                interval = float(line[53:62])
                self.values['Kinetic Energy'] = Value(value,unit,interval)
            elif 'Temperature' in line:
                value = float(line.split()[1])
                unit  = line.split()[2]
                interval = float(line[53:62])
                self.values['Temperature'] = Value(value,unit,interval)
            elif 'Pressure' in line:
                value = float(line.split()[1])
                unit  = line.split()[2]
                interval = float(line[53:62])
                self.values['Pressure'] = Value(value,unit,interval)
            elif 'Density' in line:
                value = float(line.split()[1])
                unit  = line.split()[2]
                interval = float(line[53:62])
                self.values['Density'] = Value(value,unit,interval)
            elif 'Current Time' in line :
                value = float(line.split()[2])
                unit  = line.split()[3]
                self.values['Current Time'] = Value(value,unit)
            elif 'Current Potential' in line:
                value = float(line.split()[2])
                unit  = line.split()[3]
                self.values['Current Potential'] = Value(value,unit)
            elif 'Current Kinetic' in line:
                value = float(line.split()[2])
                unit  = line.split()[3]
                self.values['Current Kinetic'] = Value(value,unit)
            elif 'Lattice Lengths' in line:
                x = float(line.split()[2])
                y = float(line.split()[3])
                z = float(line.split()[4])
                self.values['Lattice Lengths'] = (x,y,z)
            elif 'Lattice Angles' in line:
                x = float(line.split()[2])
                y = float(line.split()[3])
                z = float(line.split()[4])
                self.values['Lattice Angles'] = (x,y,z)
            elif 'Frame Number' in line:
                value = int(line.split()[2])
                self.values['Frame Number'] = value
            elif 'Coordinate File' in line:
                self.values['Coordinate File'] = line.split()[2]


class TinkerLog:
    def __init__(self,filename):
        self.avg_points = list()
        self.ins_points = list()
        for lines in TinkerLog.next_point(open(filename)):
            point = Point(lines)
            if point.type == 'avg':
                self.avg_points.append(point)
            elif point.type == 'ins' :
                self.ins_points.append(point)
        self.avg_values = dict()
        self.ins_values = dict()
        for point in self.avg_points:
            for key in point.values.keys():
                if self.avg_values.has_key(key):
                    self.avg_values[key].append(point.values[key])
                else:
                    self.avg_values[key] = list()
                    self.avg_values[key].append(point.values[key])
        for point in self.ins_points:
            for key in point.values.keys():
                if self.ins_values.has_key(key):
                    self.ins_values[key].append(point.values[key])
                else:
                    self.ins_values[key] = list()
                    self.ins_values[key].append(point.values[key])

    def debug(self):
        for key in self.avg_values.keys():
            print key

    def plot_avg(self):
        xkey  =  'Simulation Time'
        xvalues = list()
        xunit = self.avg_values[xkey][0].unit
        for tmp in self.avg_values[xkey]:
            xvalues.append(tmp.value)
        for key in self.avg_values.keys():
            filename = "%s.avg.png"%key
            values = list()
            unit = self.avg_values[key][0].unit
            for tmp in self.avg_values[key]:
                values.append(tmp.value)
            plt.cla()
            plt.plot(xvalues,values)
            plt.xlabel("%s (%s)"%(xkey,xunit))
            plt.ylabel("%s (%s)"%(key,unit))
            plt.title("Data from %s"%infile)
            plt.savefig(filename)

    @staticmethod 
    def next_point(ifp):
        current_lines = list()
        current_type = None
        for line in ifp:
            if len(line.strip()) == 0 or line.strip()[0] == '#' :
                continue
            if 'Molecular Dynamics Trajectory' in line:
                continue

            if 'Average Values for' in line or 'Instantaneous Values for ' in line :
                if len(current_lines) == 0 :
                    current_lines.append(line)
                else:
                    yield current_lines
                    current_lines = list()
                    current_lines.append(line)
            else:
                current_lines.append(line)
    
                
a = TinkerLog(infile)
a.plot_avg()

        
        
