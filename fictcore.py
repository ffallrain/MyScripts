#!/usr/bin/python

from bs4 import BeautifulSoup
import re,sys
import flib

reload(sys)
sys.setdefaultencoding('utf-8')

def get(req):
	output=''
	url="http://dict.cn/"+req
	content=flib.furlopen(url)

	soup=BeautifulSoup(BeautifulSoup(content).prettify(),'html.parser') # haha
	sectiondef=soup.find(class_="section def")

	if sectiondef==None:
		output=output+"  Sorry , I didn't find such a word. Do you mean:"
		h3s=soup.find(class_="section unfind").findAll("li",style=False)
		content=re.sub(re.compile(r"\s*\n+\s*</a>\s*\n+\s*",re.S)," : ",str(h3s)[1:-1])
		content=re.sub(re.compile(r"<.*?>",re.S),"",content)
		content=re.sub(re.compile(r"\s*\n+\s*,\s*\n+",re.S),"\n",content)
		output=output+content
	else:
		phonetic=soup.find(class_="phonetic")
		if hasattr(phonetic,"text"):
			enus=phonetic.find(lang="EN-US")
			if hasattr(enus,"text"):
				output=output+enus.text
	
		h3s=sectiondef.findAll(re.compile(r"h3|li"),style=False)
		for h3 in h3s:
			output=output+h3.text
		output=re.sub(r"\n+\s*\n+","\n",output)

	return output[1:-1]

