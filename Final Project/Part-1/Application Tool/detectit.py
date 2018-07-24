"""
Detect-it v1.0
By Mohamed Yilmaz
Project Start date: 20/05/2017
"""

from bs4 import BeautifulSoup
from xml.sax import *   
from urllib.request import URLError, HTTPError
import urllib
import time
import re,sys,os
import argparse
from argparse import ArgumentParser
from crawler import database, database_css, database_js
from crawler import crawler, cj, allowedExtensions
import warnings
import pickle

COOKIEFILE = 'cookies.lwp'     
import os.path
txdata = None
refererUrl = "http://google.com/?q=you"
txheaders = {'User-agent' : 'Detect-it v1.0 (X11; U; Linux i686; en-US; rv:1.7)', 'Referer' : refererUrl}

import http.cookiejar
import urllib.request
urlopen = urllib.request.urlopen
Request = urllib.request.Request

def normalize_whitespace(text):
	return ' '.join(text.split())

def clear_whitespace(text):
	return text.replace(' ','')

confFile = False
confUrl  = ""
confCrawler = False
confActions = []
confInfos   = {}

class ConfHandler(ContentHandler):
	def __init__(self):
		global confFile
		confFile = True
		self.inSite    = False
		self.inScan    = False
		self.inCrawler  = False
		self.inUrl     = False
		self.inAction  = False
		self.string = ""
		self.listActions = ["xss"]
	def startElement(self, name, attrs):
		global confUrl,confInfos
		self.string = ""
		if name == 'site':
			self.inSite = True
		if name == 'crawler' and self.inSite:
			self.inCrawler = True
		if name == 'scan' and self.inSite:
			self.inScan = True
		elif self.inSite and name == 'url':
			self.inUrl = True
			confUrl = ""
		elif self.inScan and name in self.listActions:
			self.inAction = True
			if 'info' in attrs.keys():
				confInfos[name] = attrs.getValue('info')
	def characters(self, ch):
		if self.inSite:
			self.string = self.string + ch
	def endElement(self, name):
		global confUrl,confActions,confCrawler
		if name == 'url' and self.inUrl:
			self.inUrl = False
			confUrl = normalize_whitespace(self.string)
		if name == 'crawler' and self.inCrawler:
			self.inCrawler = False
			confCrawler = clear_whitespace(self.string)
		if name in self.listActions and self.inScan and not name in confActions:
			confActions.append(name)
		if name == 'site' and self.inSite:
			self.inSite = False

attack_list = { }
class AttackHandler(ContentHandler):
	def __init__(self):
		global attack_list
		attack_list = {}
		self.inElmt = False
		self.inCode = False
		self.inName = False
		self.sName   = ""
		self.code   = ""
	def startElement(self, name, attrs):
		if name == 'attack':
			self.inElmt = True
		elif name == 'code':
			self.inCode = True
			self.code = ""
		elif name == "name":
			self.inName = True
			self.sName = ""
	def characters(self, ch):
		if self.inCode:
			self.code = self.code + ch
		elif self.inName:
			self.sName = self.sName + ch
	def endElement(self, name):
		global attack_list
		if name == 'code':
			self.inCode = False
			self.code = normalize_whitespace(self.code)
		if name == 'name':
			self.inName = False
			self.sName = normalize_whitespace(self.sName)
		if name == 'attack':
			self.inElmt = False

			if not (self.sName in attack_list.keys()):
				attack_list[self.sName] = []
			attack_list[self.sName].append(self.code)

class LogHandler:
	def __init__(self, fileName):
		self.stream = None
		try:
			self.stream = open(fileName, 'w')
		except IOError:
			print("Error during the construction of the log system")
			return
		self.stream.write("# Log from Detect-it.py\n")
	def __le__(self, string):
		self.stream.write(string + '\n')
		self.stream.flush()
	def __del__(self):
		self.stream.close()

log = LogHandler('detectit.log')

def unescape(s):
	
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("&quot;", "\"")
	s = s.replace("&apos;","'")
	s = s.replace("&amp;", "&")
	return s


def single_urlencode(text):
   
   code = urllib.parse.urlencode({'codecodecode':text})
   
   code = code[13:]
   code = code.replace('%5C0','%00')
   return code

def getContent_GET(url,param,injection):
	global log
	
	newUrl = url
	ret = None
	if url.find('?') < 0:
		if url[len(url)-1] != '/' and not allowedExtensions(url):
			url += '/'
		newUrl = url + '?' + param + '=' + single_urlencode(str(injection))
	else:
		newUrl = url + '&' + param + '=' + single_urlencode(str(injection))
	try:
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		urllib.request.install_opener(opener)
		log <= ( newUrl)
		req = Request(newUrl, None, txheaders) 
		ret = urllib.request.urlopen(req)                    
		ret = urllib.request.urlopen(req)                    
	except HTTPError as e:
		log <= ( 'The server could not fulfill the request.')
		log <= ( 'Error code: %s' % e.code)
		return None
	except URLError as e:
		log <= ( 'We failed to reach a server.')
		log <= ( 'Reason: %s' % e.reason)
		return None
	except IOError:
		log <= ( "Cannot open: %s" % url)
		return None
	return ret


def getContentDirectURL_GET(url, string):
	global log
	
	ret = ""
	try:
		if len(string) > 0:
			if url[len(url)-1] != '/' and url.find('?') < 0  and not allowedExtensions(url):
				url += '/'
			url = url + "?" + (string)
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		urllib.request.install_opener(opener)
		log <= ( url)
		req = Request(url, None, txheaders) 
		ret = urllib.request.urlopen(req)   
	except HTTPError as e:
		log <= ( 'The server could not fulfill the request.')
		log <= ( 'Error code: %s' % e.code)
		return None
	except URLError as e:
		log <= ( 'We failed to reach a server.')
		log <= ( 'Reason: %s' % e.reason)
		return None
	except IOError:
		log <= ( "Cannot open: %s" % url)
		return None
	return ret


def getContent_POST(url,param,injection):
	global log
	
	txdata = urllib.urlencode({param: injection})
	ret = None
	try:
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		urllib.request.install_opener(opener)
		log <= ( url)
		log <= ( txdata)
		req = Request(url, txdata, txheaders)  
		ret = urllib.request.urlopen(req)      
		ret = urllib.request.urlopen(req)      
	except HTTPError as e:
		log <= ( 'The server could not fulfill the request.')
		log <= ( 'Error code: %s' % e.code)
		return None
	except URLError as e:
		log <= ( 'We failed to reach a server.')
		log <= ( 'Reason: %s' % e.reason)
		return None
	except IOError:
		log <= ( "Cannot open: %s" % url)
		return None
	return ret


def getContentDirectURL_POST(url,allParams):
	global log
	
	txdata = urllib.urlencode(allParams)
	ret = None
	try:
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		urllib.request.install_opener(opener)
		log <= ( url)
		log <= ( txdata)
		req = Request(url, txdata, txheaders)  
		ret = urlopen(req)                     
		ret = urlopen(req)                     
	except HTTPError as  e:
		log <= ( 'The server could not fulfill the request.')
		log <= ( 'Error code: %s' % e.code)
		return None
	except URLError as e:
		log <= ( 'We failed to reach a server.')
		log <= ( 'Reason: %s' % e.reason)
		return None
	except IOError:
		log <= ( "Cannot open: %s" % url)
		return None
	return ret


def ld(a, b): 
	n, m = len(a), len(b)
	if n > m:
		
		a,b = b,a
		n,m = m,n
	current = range(n+1)
	for i in range(1,m+1):
		previous, current = current, [i]+[0] * m
		for j in range(1, n+1):
			add, delete = previous[j] + 1, current[j-1] + 1
			change = previous[j-1]
			if a[j-1] != b[i-1]:
				change +=1
			current[j] = min(add, delete, change)
	return current[n]


def partially_in(object, container, url = "IMPOSSIBLE_URL", two_long = False):
	
	try:
		if object in container and url not in container:
			return True
	except TypeError:
		return False
	if not two_long:
		
		dist = ld(object, container)
		
		b1 = int(len(object) - len(object) / 4)
		b2 = int(len(object) + len(object) / 4)
		
		length = abs(len(container)- dist)
		if b1 < length and length < b2:
			return True
	else:
		
		dist = ld(object, container)
		
		b1 = int(len(object) - len(object) / (len(object) + 1))
		b2 = int(len(object) + len(object) / (len(object) + 1))
		
		length = abs(len(container)- dist)
		if b1 < length and length < b2:
			return True
	return False


def load_definition(fileName):
	
	global attack_list
	attack_list = {}
	parser = make_parser()
	xss_handler = AttackHandler()
	
	parser.setContentHandler(xss_handler)
	parser.parse(fileName)


def	setDatabase(localDatabase):
	global database
	database = {}
	database = localDatabase


def investigate(url, what = "xss"):
	global attack_list
	
	localDB = None
	if what == "xss":
		from xss import process
		load_definition('xssAttacks.xml')
		localDB = database
	
	process(url, localDB, attack_list)


	for index, cookie in enumerate(cj):
		print ('[Cookie]\t', index, '\t:\t', cookie)
	cj.save(COOKIEFILE)


def active_link(s):
	pos = s.find('http://')
	if pos < 1:
		return s
	else:
		print (pos, len(s), s[pos:len(s)])
		url = s[pos:len(s)]
		newStr = s[0:pos-1] + "<a href='" +url + "'>" + urllib.unquote(url) + "</a>"
		return newStr
	return s

def createStructure():
	try:
		os.mkdir("results")
	except OSError as e :
		a=0
	try:
		os.mkdir("local")
	except OSError as e :
		a=0
	try:
		os.mkdir("local/js")
	except OSError as e :
		a=0
	try:
		os.mkdir("local/css")
	except OSError as e :
		a=0

if __name__ == '__main__':

        choice=input("Do you want to scan from the configuration file or manually enter the input (Y/N):")
        if choice == 'Y' or choice == 'y':
                archives_url=input("Enter the url you wish to test: ")
                print("Testing for XSS vulnerablility...")

        else:
                try:
                        f = open("detectit.conf.xml", 'r')
                except IOError:
                        print ("No arguments are given....Please setup the xml file to start scanning")
                        sys.exit(1)
                parser = make_parser()
                conf_handler = ConfHandler()
                
                parser.setContentHandler(conf_handler)
                parser.parse("detectit.conf.xml")

                option_url    = confUrl
                option_crawler = confCrawler
                option_xss    = "xss" in confActions
                
	
                archives_url = "http://localhost"
                if option_url:
                        archives_url = option_url
                root = archives_url

                createStructure()
                depth = 1
                try:
                        depth = int(option_crawler.strip().split()[0])
                except (ValueError, IndexError,AttributeError):
                        depth = 0

                try:
                        try:
                                crawler(archives_url, depth)
                        except IOError as e :
                                print ("Cannot open the url = %s" % archives_url)
                                print (e.strerror)
                                sys.exit(1)
                        if len(database.keys()) < 1:
                                print ("No information found!")
                                sys.exit(1)
                        else:
                                print ("Starting investigation for the given URL...Please wait...")

                        if option_xss:
                                investigate(archives_url)
                        
                except KeyboardInterrupt:
                        print ("Oops...exited!")




















