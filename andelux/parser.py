#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,re
from urlparse import urlparse
#from sgmllib import SGMLParser
from BeautifulSoup import BeautifulSoup
import codecs, chardet
from kitchen.text.converters import getwriter, to_bytes, to_unicode

from andelux.path import PATHS
import api.log
# LOG OBJECT
log = api.log.Logger("andelux.log", "parser")
import api.link
import api.page



class Parser():
	host = ''
	scheme = 'http'
	links = []
	links_internal = 0
	links_external = 0
	id_page = 0

	def __init__(self, id_page, url, urlhash):
		self.id_page = id_page
		self.url = url
		self.urlhash = urlhash
		self.links = []
		self.links_internal = 0
		self.links_external = 0

		o = urlparse( url )
		if o.scheme == '': o.scheme = 'http'
		self.scheme = o.scheme
		self.host = o.hostname

		filename = PATHS['ROOT'] + '/cache/' + o.hostname + '/' + urlhash + '/index.html'

		if os.path.exists( filename ):
			log.add( 'parsing URL %s' % url )
			
			# TODO: borrar todos los enlaces de esta página
			
			f = codecs.open( filename, 'r', 'utf-8' )
			data = f.read()
			f.close()

			parser = BeautifulSoup( data )
			for link in parser.findAll('a'):
				if link.has_key('href'):
					L = self.normalizeLink( {'link': link['href'], 'keywords':link.string} )
					self.addLink( L )
				
			# ponemos estatus = parsed
			api.cache.setStatus(self.id_page, 'parsed')
			
			log.add( 'page parsed with %d internal and %d external links (total = %d)' % (self.links_internal, self.links_external, len(self.links)) )
				

	def addLink(self, U):
		link = U['link']
		
		o = urlparse( link )
		if o.scheme == 'http' or o.scheme == 'https':
			if not link in self.links:
				self.links.append( link )
				if o.hostname == self.host:
					# internal
					self.links_internal += 1
					where = 'internal'
					#print "[+] LINKS INTERNAL: %s | %s" % (U['keywords'], link, )
				else:
					# external
					self.links_external += 1
					#print "[+] LINKS EXTERNAL: %s | %s" % (U['keywords'], link, )
					where = 'external'
				
				id_page_link = api.page.getIdByURL( link )
				if id_page_link > 0:
					api.link.setLink( self.id_page, id_page_link, where, U['keywords'] )
			
				
	def normalizeLink(self, U):
		link = U['link']
		
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
			
		U['link'] = url
		
		return U


def parser(id_page, url, urlhash):
	return Parser(id_page, url, urlhash)
	
