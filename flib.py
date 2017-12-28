#!/usr/bin/python
import urllib2

def furlopen(url):
	for i in [1,2,3]:
		try:
			content=urllib2.urlopen(url).read()
			return content
		except:
			pass

def dist_coord(a,b):
    s = (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2
    return s**0.5
