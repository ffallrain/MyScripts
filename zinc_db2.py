#!/usr/bin/python
import sys,os
import urllib
import flib
from bs4 import BeautifulSoup
import re
reload(sys)
sys.setdefaultencoding('utf-8')


pat = re.compile(r'.*?"(.*?)".*')
def ana_url(url):
    content = flib.furlopen(url)
    soup = BeautifulSoup(BeautifulSoup(content).prettify()) # haha

    for line in  str(soup).split('\n'):
        if 'db2' in line and 'files.docking.org/protomers' in line:
            match = re.match(pat,line)
            return match.group(1)
def down_db2(index):
    url = r'http://zinc15.docking.org/substances/ZINC%012d/'%index
    link = ana_url(url)
    os.system('wget %s'%link)
