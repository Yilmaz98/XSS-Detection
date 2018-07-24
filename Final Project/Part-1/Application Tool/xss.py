
import sys
from detectit import getContent_POST, getContent_GET
from detectit import getContentDirectURL_GET, getContentDirectURL_POST
import urllib
from detectit import single_urlencode, partially_in

def detect_xss(instance, output):
	if unescape(instance.encode('UTF-8')) in output:
		return True
	elif partially_in(unescape(instance.encode('UTF-8')), output):
		return True
	return False
"""
def decode(s):
	unescape(s.decode('utf-8'))
"""	
def unescape(s):
	
	s = s.replace(b"&lt;", b"<")
	s = s.replace(b"&gt;", b">")
	s = s.replace(b"&quot;", b"\"")
	s = s.replace(b"&apos;",b"'")
	s = s.replace(b"&amp;", b"&")
	return s

def generateOutput(url, gParam, instance,method,type):
	astr = "<xss>\n\t<method>%s</method>\n\t<url>%s</url>\n\t<parameter name='%s'>%s</parameter>\n\t<type name='XSS Injection Type'>%s</type>"  % (method,url,gParam,str(instance),type)
	if method in ("get","GET"):
		
		p = (url+"?"+gParam+"="+single_urlencode(str(instance)))
		astr += "\n\t<result>%s</result>" % p
	astr += "\n</xss>\n"
	return astr

def generateOutputLong(url, urlString ,method,type, allParams = {}):
	astr = "<xss>\n\t<method>%s</method>\n\t<url>%s</url>\n\t<type name='XSS Injection Type'>%s</type>"  % (method,url,type)
	if method in ("get","GET"):
		
		p = (url+"?"+urlString)
		astr += "\n\t<result>%s</result>" % (p)
	else:
		astr += "\n\t<parameters>"
		for k in allParams:
			astr += "\n\t\t<parameter name='%s'>%s</parameter>" % (k, allParams[k])
		astr += "\n\t</parameters>"
	astr += "\n</xss>\n"
	return astr


def permutations(L):
	if len(L) == 1:
		yield [L[0]]
	elif len(L) >= 2:
		(a, b) = (L[0:1], L[1:])
		for p in permutations(b):
			for i in range(len(p)+1):
				yield b[:i] + a + b[i:]

def process(urlGlobal, database, attack_list):
	plop = open('results/xss_foundAttacks.xml','w')
	plop.write("<xssAttacks>\n")

	for u in database.keys():
		if len(database[u]['GET']):
			print ("Method = GET ", u)
			for gParam in database[u]['GET']:
				for typeOfInjection in attack_list:
					for instance in attack_list[typeOfInjection]:
						if instance != "See Below":
							handle = getContent_GET(u,gParam,instance)
							if handle != None:
								output = handle.read()
								header = handle.info()
								if detect_xss(str(instance),output):
									
									plop.write(generateOutput(u,gParam,instance,"GET",typeOfInjection))
			
			if len(database[u]['GET'].keys()) > 1:
				for typeOfInjection in attack_list:
					for instance in attack_list[typeOfInjection]:
						url = ""
						for gParam in database[u]['GET']:
							url += ("%s=%s&" % (gParam, single_urlencode(str(instance))))
						handle = getContentDirectURL_GET(u,url)
						if handle != None:
							output = handle.read()
							if detect_xss(str(instance),output):
								
								plop.write(generateOutputLong(u,url,"GET",typeOfInjection))
		if len(database[u]['POST']):
			print ("Method = POST ", u)
			for gParam in database[u]['POST']:
				for typeOfInjection in attack_list:
					for instance in attack_list[typeOfInjection]:
						if instance != "See Below":
							handle = getContent_POST(u,gParam,instance)
							if handle != None:
								output = handle.read()
								header = handle.info()
								if detect_xss(str(instance),output):
									
									plop.write(generateOutput(u,gParam,instance,"POST",typeOfInjection))
			
			if len(database[u]['POST'].keys()) > 1:
				for typeOfInjection in attack_list:
					for instance in attack_list[typeOfInjection]:
						allParams = {}
						for gParam in database[u]['POST']:
							allParams[gParam] = str(instance)
						handle = getContentDirectURL_POST(u,allParams)
						if handle != None:
							output = handle.read()
							if detect_xss(str(instance), output):
							
								plop.write(generateOutputLong(u,url,"POST",typeOfInjection, allParams))
	plop.write("\n</xssAttacks>\n")	
	plop.close()
	return ""
