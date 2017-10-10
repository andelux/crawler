#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import api.cache
import api.log
from urlparse import urlparse
import hashlib
import pycurl
import time
import shutil
import difflib
import chardet
from kitchen.text.converters import getwriter, to_bytes, to_unicode


# LOG OBJECT
log = api.log.Logger("andelux.log", "fetcher")


'''
cacher(url):
Actualiza la caché de una URL

- la URL debe estar normalizada
'''
def fetcher(url, urlhash):
	log.add('fetching URL: %s' % url)

	o = urlparse( url )
	dirname = 'cache/' + o.hostname + '/' + urlhash + '/'
	
	try:
		os.makedirs( dirname )
	except OSError:
		None

	# HTML
	data = dirname + 'index.html'
	previous = dirname + 'previous.html'
	# Cabeceras HTTP
	headers = dirname + 'headers'
	# Metadata: tiempo de descarga, ...
	metadata = dirname + 'metadata'
	
	try:
		# guardamos los datos existentes
		if os.path.exists( data ):
			shutil.copy2( data, previous )
	
		# creamos de nuevo los ficheros de datos
		fd = open(data, 'w')
		fh = open(headers, 'w')
		fm = open(metadata, 'w')
		
		# preparamos la petición de página
		c = pycurl.Curl()
		c.setopt(pycurl.URL, url)
		c.setopt(pycurl.HEADER, 0)
		c.setopt(pycurl.HTTPGET, 1)
		c.setopt(pycurl.HTTPHEADER, ["Accept: text/html, application/xhtml+xml, text/plain"])
		c.setopt(pycurl.WRITEFUNCTION, fd.write)
		c.setopt(pycurl.HEADERFUNCTION, fh.write)
		c.setopt(pycurl.FOLLOWLOCATION, 0)
		c.setopt(pycurl.USERAGENT, 'AndeluxBot/0.1a')
		c.setopt(pycurl.TIMEOUT, 15)
		
		# obtenemos datos
		# ejecutamos con timer
		time_start = time.time()
		c.perform()
		time_end = time.time()
		time_elapsed = time_end - time_start
		fm.write('Time-Elapsed: %.4f\n' % time_elapsed)
		
		# HTTP code
		http_code = c.getinfo(pycurl.HTTP_CODE)
		
		# cerramos ficheros
		c.close()
		fd.close()
		fh.close()
		fm.close()
		
		# convertimos datos en utf-8
		fd = open( data, 'r' )
		html = fd.read()
		fd.close()
		enc = chardet.detect( html )
		if not enc is None and not enc['encoding'] is None and enc['encoding'].lower() != 'utf-8':
			#html = to_unicode(html, 'utf-8')
			html = to_unicode(html, enc['encoding'])
			fd = open( data, 'w' )
			fd.write( to_bytes( html ) )
			fd.close()
		
		
		# diff
		new_diff = diff( data, previous )
		
		# cargamos cabeceras
		headers_data = {}
		f = open(headers, 'r')
		for line in f:
			line = line.strip().split(':', 1)
			if len(line) == 2:
				header_name = line[0].strip().lower()
				header_value = line[1].strip()
				headers_data[header_name] = header_value
		
		# procesamos según código HTTP
		if http_code == 200:
			
			# content-type
			contenttype = ''
			charset = ''
			if headers_data.has_key('content-type'):
				CT = headers_data.get('content-type').lower().split(';')
				contenttype = CT[0].strip()
				if len(CT) > 1:
					CS = CT[1].strip().split('charset=')
					if len(CS) > 1:
						charset = CS[1].strip()
				
			# log
			log.add('fetched URL: %s - %.4fs - %.2f - %s' % (contenttype, time_elapsed, new_diff, url))
			
			return (http_code, contenttype, charset, '%.4f' % time_elapsed, new_diff)
			
		elif http_code == 301 or http_code == 302:

			#print url
			#print urlhash
			#print headers_data

			# location
			location = None
			if headers_data.has_key('location'):
				location = headers_data['location']
				
			# cambiamos la página
			return (http_code, location)

		else:
			# error
			return (http_code, None)
		
	except IOError:
		return None


def diff(a, b):
	if not os.path.exists( b ):
		return 100

	#out = []
	fa = open(a, 'r')
	a = fa.readlines()
	fa.close()
	fb = open(b, 'r')
	b = fb.readlines()
	fb.close()
	
	# número total de líneas
	total_size = len(a)
	if total_size == 0:
		return 0

	# número de líneas modificadas
	total_new = 0
	
	s = difflib.SequenceMatcher(None, a, b)
	for e in s.get_opcodes():
		#print e
		
		if e[0] == "replace":
			total_new += e[2] - e[1]
			#out.append('<del class="diff modified">'+''.join(a[e[1]:e[2]]) + '</del><ins class="diff modified">'+''.join(b[e[3]:e[4]])+"</ins>")
		elif e[0] == "delete":
			total_new += e[2] - e[1]
			#out.append('<del class="diff">'+ ''.join(a[e[1]:e[2]]) + "</del>")
		elif e[0] == "insert":
			total_new += e[4] - e[3]
			#out.append('<ins class="diff">'+''.join(b[e[3]:e[4]]) + "</ins>")
		elif e[0] == "equal":
			None
			#out.append(''.join(b[e[3]:e[4]]))
		else: 
			raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
	#return ''.join(out)
	return (total_new / total_size) * 100



if __name__ == '__main__':
	if len(sys.argv) > 1:
		PATHS['ROOT'] = os.path.realpath('..')
		url = sys.argv[1]
		urlhash = hashlib.sha1(url).hexdigest()
		fetcher( url, urlhash )


