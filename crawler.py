#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import feedparser
import re, time
import subprocess
from sgmllib import SGMLParser
import htmlentitydefs
import urllib
from urlparse import urlparse

'''
BOT FETCHER
'''
class AndeluxURLopener(urllib.FancyURLopener):
	version = "AndeluxBot/1.0a"
   
urllib._urlopener = AndeluxURLopener()

'''
BOT PARSER
'''
class URLLister(SGMLParser):
	def reset(self):                              
		SGMLParser.reset(self)
		self.urls = []

	def start_p(self, attrs):
		return None

	def start_a(self, attrs):
		href = [v for k, v in attrs if k=='href']  
		if href:
			self.urls.extend(href)


def download(url, filename):
	try:
		urllib.urlretrieve(url, filename)
		return filename
	except urllib.ContentTooShortError:
		return None
	except IOError:
		return None
		
		
class AndeluxCrawler():
	host = ''
	scheme = 'http'
	links_internal = []
	links_external = []
	links_parsed = []
	links_pending = []
	
	def init(self, url):
		o = urlparse( url )
		if o.scheme == '': o.scheme = 'http'
		self.scheme = o.scheme
		self.host = o.hostname
		
		self.hostpath = 'cache/' + self.host
		
		try:
			os.makedirs( self.hostpath )
		except OSError:
			None
		
		link = self.scheme + '://' + self.host
		print "[i] PARSING HOME: %s\n" % link
		self.parse( link, self.hostpath + '/index.html' )
		
		while len(self.links_pending) > 0:
			print "[-] LINKS: PARSED = %d | PENDING = %d | INTERNAL = %d | TOTAL = %d\n" % (len(self.links_parsed), len(self.links_pending), len(self.links_internal), len(self.links_parsed) + len(self.links_pending))

			link = self.links_pending.pop(0)
			self.links_parsed.append( link )
			print "[*] PARSING: %s\n" % link
			
			if self.isInternalLink( link ):
				o = urlparse( link )
				filename = self.hostpath + o.path

				try:
					os.makedirs( filename )
				except OSError:
					None

				if not filename.endswith('/'): filename += '/'
				filename += 'index.html'
				
				self.parse( link, filename )
				
				
		
	def isInternalLink(self, link):
		o = urlparse( link )
		if o.scheme == 'http' or o.scheme == 'https':
			if o.hostname == self.host:
				return True
		return False
		
	def addLink(self, link):
		o = urlparse( link )
		if o.scheme == 'http' or o.scheme == 'https':
			if o.hostname == self.host:
				# internal
				if not link in self.links_internal:
					self.links_internal.append( link )
					print "[+] LINKS INTERNAL: %s\n" % link
			else:
				# external
				if not link in self.links_external:
					self.links_external.append( link )
					print "[+] LINKS EXTERNAL: %s\n" % link
				
			# pending list
			if not link in self.links_parsed and not link in self.links_pending:
				self.links_pending.append( link )
				print "[+] LINKS PENDING: %s\n" % link

	
	
	def normalizeLink(self, link):
		o = urlparse( link )
		scheme = o.scheme
		path = o.path
		query = o.query

		A = o.netloc.split(':')
		host = A[0]
		if len(A) == 1:
			port = 80
		else:
			if A[1] == '':
				port = 80
			else:
				port = int(A[1])

		if scheme == '': scheme = self.scheme
		if host == '': host = self.host
		
		if not path.startswith('/'): path = '/' + path
		
		url = scheme + '://'
		
		if scheme != 'mailto':
			url += host
			if port != 80:
				url += ':' + str(port)
			
		url += path
		
		if query != '':
			url += '?' + query
			
		return url
		
	def parse(self, url, filename):
		if not os.path.exists( filename ):
			download( url, filename )
			
		if os.path.exists( filename ):
			f = open(filename, 'r')
			parser = URLLister()
			parser.feed( f.read() )
			f.close()
			parser.close()
			
			for link in parser.urls:
				link = self.normalizeLink( link )
				self.addLink( link )
				#print link + "\n"


url = 'http://javierperez.eu/'

if len(sys.argv) > 1:
	url = sys.argv[1]

print "CRAWLING %s\n" % url

crawler = AndeluxCrawler()
crawler.init( url )
			
		
		
