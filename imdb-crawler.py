# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 23:54:13 2016

@author: abhis
"""

import requests

from bs4 import BeautifulSoup
import unicodedata
import sys

url = "http://www.imdb.com/title/tt0816692/reviews"

source_code = requests.get(url)

plain_text = source_code.text

soup = BeautifulSoup(plain_text,"lxml")
fi = open("test.txt","w")
fi.truncate()
fi.close()
for link in soup.findAll('p'):
    paragraph = link.string
    a = unicodedata.normalize('NFKD', unicode(paragraph)).encode('ascii','ignore')
    #print paragraph
    sys.stdout=open("test.txt","app")
    print a
sys.stdout.close()