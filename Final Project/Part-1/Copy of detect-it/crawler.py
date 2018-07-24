import funcTools
import urllib
import time
import re,sys,os,string
from bs4 import BeautifulSoup,SoupStrainer
from urllib.request import URLError, HTTPError
COOKIEFILE = 'cookies.lwp'         
import os.path
cj = None
ClientCookie = None
cookielib = None

import http.cookiejar
urlopen = urllib.request.urlopen
cj = http.cookiejar.LWPCookieJar()       
Request = urllib.request.Request
txdata = None
refererUrl = "http://google.com/?q=you!"
txheaders = {'User-agent' : 'Detect-it v1.0 (X11; U; Linux i686; en-IN; rv:1.7)', 'Referer' : refererUrl}

allowed=['php','html','htm','xml','xhtml','xht','xhtm',
         'asp','aspx','msp','mspx','php3','php4','php5','txt','shtm',
	    'shtml','phtm','phtml','jhtml','pl','jsp','cfm','cfml','do','py',
		'js', 'css']
database     = {}
database_url = []
database_css = []
database_js  = []
database_ext = []
local_url    = []
dumb_params  = [] 
root = "http://localhost"


outCrawlerFile = None

_urlEncode = {}
for i in range(256):
	_urlEncode[chr(i)] = '%%%02x' % i
for c in string.ascii_letters + string.digits + '_,.-/':
	_urlEncode[c] = c
_urlEncode[' '] = '+'


def urlEncode(s):
	return string.join(map(lambda c: _urlEncode[c], list(s)), '')



def urlDecode(s):
	mychr = chr
	atoi = string.atoi
	parts = string.split(string.replace(s, '+', ' '), '%')
	for i in range(1, len(parts)):
		part = parts[i]
		parts[i] = mychr(atoi(part[:2], 16)) + part[2:]
	return string.join(parts, '')



def htmlencode(s):
                s = s.replace("&", "&amp;")
                s = s.replace("<", "&lt;")
                s = s.replace(">", "&gt;")
                s = s.replace("\"","&quot;")
                s = s.replace("'", "&apos;")
                return s



def htmldecode(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("&quot;","\"")
	s = s.replace("&apos;","'")
	s = s.replace("&amp;","&")
	return s



def getContentDirectURL_GET(url, string):
	ret = ""
	try:
		if len(string) > 0:
			url = url + "?" + (string)
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		urllib.request.install_opener(opener)
		req = Request(url, None, txheaders) 
		ret = urllib.request.urlopen(req)   
	except HTTPError as e:
		return
	except URLError as e:
		return
	except IOError:
		return
	return ret



def scan(currentURL):
	try:
		archives_hDl = getContentDirectURL_GET(currentURL,'')
	except IOError:
		log <= ("IOError @ %s" % currentURL)
	try:
		htmlContent= archives_hDl.read()
	except IOError as e:
		print ("Cannot open the file,",(e.strerror))
		return
	except AttributeError:
		print ("Detect-it cannot retrieve the given url: %s" % currentURL)
		return
	parseHtmlLinks (currentURL,htmlContent)
	parseHtmlParams(currentURL,htmlContent)

def allowedExtensions(plop):
	for e in allowed:
		if '.'+e in plop:
			return True
	return False



def makeRoot(urlLocal):
	if allowedExtensions(urlLocal):
		return urlLocal[0:urlLocal.rfind('/')+1]
	return urlLocal



def giveGoodURL(href, urlLocal):
	
	if 'http://' in href or 'https://' in href:
		if urlLocal in href:
			return htmldecode(href)
		else:
			return urlLocal
	if len(href) < 1:
		return htmldecode(urlLocal)
	if href[0] == '?' and '?' not in urlLocal and not allowedExtensions(urlLocal):
		for e in allowed:
			if '.'+e in urlLocal:
				return htmldecode(urlLocal + href)
		return htmldecode(urlLocal + '/' + href)
	else:
		
		if allowedExtensions(urlLocal) or '?' in urlLocal:
			return htmldecode(urlLocal[0:urlLocal.rfind('/')+1] + href)
		else:
			return htmldecode(urlLocal + '/' + href)
	return htmldecode(href)


def dl(fileAdress, destFile):
	try:
		f =  urllib.request.urlopen(fileAdress)
		g = f.read()
		file = open(os.path.join('./', destFile), "wb")
	except IOError:
		return False
	file.write(g)
	file.close()
	return True


def removeSESSID(urlssid):
	k = urlssid.find('PHPSESSID')
	if k > 0:
		return urlssid[0:k-1]
	k = urlssid.find('sid')
	if k > 0:
		return urlssid[0:k-1]
	return urlssid

def parseHtmlLinks(currentURL,htmlContent):
	global database_url,database_js,database_css
	links = SoupStrainer('a')
	listAnchors = []
	for tag in BeautifulSoup(htmlContent, parse_only=links):
		try:
			string = str(tag).lower()
			if string.count("href") > 0:
				listAnchors.append(tag['href'])
		except TypeError:
			continue
		except KeyError:
			continue

	for a in listAnchors:
		goodA = giveGoodURL(a,currentURL)
		goodA = removeSESSID(goodA)
		if (root in goodA) and (goodA not in database_url):
			database_url.append(goodA)

	
	script = SoupStrainer('script')
	
	listScripts = []
	for tag in BeautifulSoup(htmlContent, parse_only=script):
		try:
			string = str(tag).lower()
			if string.count("src") > 0 and string.count(".src") < 1:
				listScripts.append(tag['src'])
		except TypeError:
			continue
		except KeyError:
			continue

	for a in listScripts:
		sc = giveGoodURL(a,currentURL)
		if sc not in database_js:
			database_js.append(sc)
		if sc == currentURL:
			
			database_ext.append(sc)
	parseJavaScriptCalls()

	link = SoupStrainer('link')
	
	listLinks = []
	for tag in BeautifulSoup(htmlContent, parse_only=link):
		try:
			string = str(tag).lower()
			if string.count("href") > 0:
				listLinks.append(tag['href'])
		except TypeError:
			continue
		except KeyError:
			continue

	for a in listLinks:
		sc = giveGoodURL(a,currentURL)
		if sc not in database_css:
			database_css.append(sc)
	return True

jsChars = ["'",'"']

def rfindFirstJSChars(string):
	b = [string.rfind(k) for k in jsChars]
	return max(b)

regDumbParam = re.compile(r'(\w+)')
regDumbParamNumber = re.compile(r'(\d+)')

jsParams = ["'",'"','=','+','%','\\',')','(','^','*','-']

def cleanListDumbParams(listDumb):
	newDumbList = []
	for w in listDumb:
		w = w.replace(' ','')
		w = w.replace('\n','')
	
		if len(w) > 0 and regDumbParam.match(w) and not regDumbParamNumber.match(w):
			newDumbList.append(w)
	return newDumbList

def unique(L):
	noDupli=[]
	[noDupli.append(i) for i in L if not noDupli.count(i)]
	return noDupli

def flatten(L):
	if type(L) != type([]):
		return [L]
	if L == []:
		return L
	return funcTools.reduce(lambda L1,L2:L1+L2,map(flatten,L))


def parseJavaScriptContent(jsContent):
	global database_url, database_ext, dumb_params
	for l in jsContent.readlines():
		for e in allowed:
			if l.count('.'+e) > 0:
	
				if l.count('http://') > 0 and l.count(root) < 1:
	
					et= '.'+e
					b1 = l.find('http://')
					b2 = l.find(et) + len(et)
					database_ext.append(l[b1:b2])
				else:
	
					et= '.'+e
					b2 = l.find(et) + len(et)
					b1 = rfindFirstJSChars(l[:b2])+1
					database_url.append(giveGoodURL(l[b1:b2],root))
		k = l.find('?')
		if k > 0:
			results = l[k:].split('?')
			plop = []
			for a in results:
				plop.append(cleanListDumbParams(regDumbParam.split(a)))
			dumb_params.append(flatten(plop))
		k = l.find('&')
		if k > 0:
			results = l[k:].split('&')
			plop = []
			for a in results:
				plop.append(cleanListDumbParams(regDumbParam.split(a)))
			plop = flatten(plop)
			dumb_params.append(flatten(plop))
	dumb_params = unique(flatten(dumb_params))

def parseJavaScriptCalls():
	global database_js
	for j in database_js:
		jsName = j[j.rfind('/')+1:]
		if not os.path.exists('local/js/' + jsName):
			dl(j,'local/js/' + jsName)
			try:
				jsContent = open('local/js/' + jsName, 'r')
			except IOError:
				continue
			parseJavaScriptContent(jsContent)
			jsContent.close()

def splitQuery(query_string):
	try:
		d = dict([x.split('=') for x in query_string.split('&') ])
	except ValueError:
		d = {}
	return d

def dict_add(d1,d2):
	d={}
	if len(d1):
		for s in d1.keys():
			d[s] = d1[s]
	if len(d2):
		for s in d2.keys():
			d[s] = d2[s]
	return d

def dict_add_list(d1,l1):
	d={}
	if len(d1):
		for s in d1.keys():
			d[s] = d1[s]
	if len(l1):
		for s in l1:
			d[s] = 'bar'
	return d

def parseHtmlParams(currentURL, htmlContent):
	global database, database_css, database_js
	for url in database_url:
		k = url.find('?')
		if k > 0:
			keyUrl = url[0:k-1]
			query = url[k+1:]
			if not keyUrl in database:
				database[keyUrl] = {}
				database[keyUrl]['GET']  = {}
				database[keyUrl]['POST'] = {}
			lG = database[keyUrl]['GET']
			lG = dict_add(lG,splitQuery(query))
			database[keyUrl]['GET']  = lG
		elif len(dumb_params) > 0:
			keyUrl = url
			if not keyUrl in database:
				database[keyUrl] = {}
				database[keyUrl]['GET']  = {}
				database[keyUrl]['POST'] = {}
			lG = database[keyUrl]['GET']
			lP = database[keyUrl]['POST']
			lG = dict_add_list(lG,dumb_params)
			lP = dict_add_list(lP,dumb_params)
			database[keyUrl]['GET']  = lG
			database[keyUrl]['POST'] = lP

	forms = SoupStrainer('form')
	input = SoupStrainer('input')
	listForm = [tag for tag in BeautifulSoup(htmlContent, parse_only=forms)]
	for f in listForm:
		method = 'GET'
		if 'method' in f or 'METHOD' in f:
			method = f['method'].upper()
		action = currentURL
		if 'action' in f or 'ACTION' in f:
			action = f['action']
		keyUrl = giveGoodURL(action,currentURL)
		listInput = [tag for tag in BeautifulSoup(str(f), parse_only=input)]
		for i in listInput:
			if not keyUrl in database:
				database[keyUrl] = {}
				database[keyUrl]['GET']  = {}
				database[keyUrl]['POST'] = {}
			try:
				value = i['value']
			except KeyError:
				value = '42'
			try:
				name = i['name']
			except KeyError:
				name = 'foo'
				value= 'bar'
				continue
			lGP = database[keyUrl][method]
			lGP = dict_add(lGP,{name : value})
			database[keyUrl][method] = lGP
	return True


def runCrawlerScan(entryUrl, depth = 0):
	global outCrawlerFile
	print ("runCrawlerScan @ ", entryUrl, " |   #",depth)
	if outCrawlerFile:
		outCrawlerFile.write("\t\t<entryURL>%s</entryURL>\n" % entryUrl)
	scan(entryUrl)
	if depth > 0 and len(database_url) > 0:
		for a in database_url:
			runCrawlerScan(a, depth-1)
		return False
	return True


def crawler(entryUrl, depth = 0):
	global root,outCrawlerFile
	if depth > 0:
		root = makeRoot(entryUrl)
	else:
		root = entryUrl
	
	try:
		f = open("local/crawlerSite.xml", 'r')
		firstLine = f.readline()
		f.close()
		if firstLine.count(root) > 0:
			alreadyScanned = True
		else:
			alreadyScanned = False
	except IOError:
		alreadyScanned = False

	print ("Starting the scan...", root)
	if depth == 0:
		scan(root)
	else:
		if not alreadyScanned:
			outCrawlerFile = open("local/crawlerSite.xml","w")
			outCrawlerFile.write("<crawler root='%s' depth='%d'>\n" % (root,depth) )
			runCrawlerScan(root, depth)
			if len(dumb_params) > 0:
				outCrawlerFile.write("<dumb_parameters>\n")
				for d in dumb_params:
					outCrawlerFile.write("\t<dumb>%s</dumb>\n" % (d))
				outCrawlerFile.write("</dumb_parameters>\n")
			outCrawlerFile.write("\n</crawler>")
			outCrawlerFile.close()
		else:
			print ("Loading the previous crawler results from 'local/crawlerSite.xml'")
			regUrl = re.compile(r'(.*)<entryURL>(.*)</entryURL>(.*)',re.I)
			regDmb = re.compile(r'(.*)<dumb>(.*)</dumb>(.*)',re.I)

			f = open("local/crawlerSite.xml", 'r')
			for l in f.readlines():
				if regUrl.match(l):
					out = regUrl.search(l)
					url = out.group(2)
					database_url.append(url)
				if regDmb.match(l):
					out = regDmb.search(l)
					param = out.group(2)
					dumb_params.append(param)
			f.close()

			for currentURL in database_url:
				try:
					archives_hDl = getContentDirectURL_GET(currentURL,'')
				except IOError:
					log <= ("IOError @ %s" % currentURL)
					continue
				try:
					htmlContent= archives_hDl.read()
				except IOError as e:
					continue
				except AttributeError as e:
					continue
				parseHtmlParams(currentURL,htmlContent)


	outCrawlerFile = open("results/scannedFiles.xml","w")
	outCrawlerFile.write("<crawler root='%s'>\n" % root)
	for i in database_url:
		outCrawlerFile.write("\t<url type='anchor'>%s</url>\n" % i)
	for i in database_js:
		outCrawlerFile.write("\t<url type='JavaScript'>%s</url>\n" % i)
	for i in database_css:
		outCrawlerFile.write("\t<url type='MetaLink'>%s</url>\n" % i)
	outCrawlerFile.write("</crawler>")
	outCrawlerFile.close()

	if len(database_ext) > 0:
		outCrawlerFile = open("results/externalCalls.xml","w")
		outCrawlerFile.write("<external>\n")
		for i in database_ext:
			outCrawlerFile.write("\t<call severity='high'>%s</call>\n" % i)
		outCrawlerFile.write("</external>")
		outCrawlerFile.close()

