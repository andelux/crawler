#!/usr/bin/env python
# -*- coding: utf-8 -*-

#if __name__ == "__main__" and __package__ is None:
#	__package__ = "andelux.api.page"
    
import hashlib
from urlparse import urlparse

from ..kitchen.text.converters import getwriter, to_bytes, to_unicode
from .. import db
import cache

import log
log = log.Logger("andelux.log", "page")

dbm = db.Db('localhost', 'andeluxsearch', 'andeluxsearch', 'andeluxsearch')

def getIdContenttype( contenttype ):
	sql = "SELECT `id` FROM as_contenttypes WHERE `contenttype` = '%s' LIMIT 1" % (contenttype, )
	_id = dbm.fetchValue( sql )

	if _id is None:
		sql = "INSERT INTO as_contenttypes (contenttype, status) VALUES ('%s', 'disabled')" % (contenttype, )
		dbm.query( sql )
		return dbm.lastrowid
	else:
		return int(_id)


def getIdCharset( charset ):
	sql = "SELECT `id` FROM as_charsets WHERE `charset` = '%s' LIMIT 1" % (charset, )
	_id = dbm.fetchValue( sql )

	if _id is None:
		sql = "INSERT INTO as_charsets (charset) VALUES ('%s')" % (charset, )
		dbm.query( sql )
		return dbm.lastrowid
	else:
		return int(_id)

def existsByHash( urlhash ):
	sql = "SELECT COUNT(*) FROM as_pages WHERE `hash` = '%s' LIMIT 1" % (urlhash, )
	count = int( dbm.fetchValue( sql ) )
	if count > 0: return True
	return False
	
def getIdByHash( urlhash ):
	sql = "SELECT `id` FROM as_pages WHERE `hash` = '%s' LIMIT 1" % (urlhash, )
	data = dbm.fetchValue( sql )
	if not data is None: return int(data)
	return None
	
def getHostIdByHost( host ):
	sql = "SELECT `id` FROM as_hosts WHERE `name` = '%s' LIMIT 1" % (host, )
	id_host = dbm.fetchValue( sql )
	if id_host is None:
		# TODO: obtener IP, id_tld y id_host_main
		sql = "INSERT INTO as_hosts (`name`, `ip`, `id_tld`, `id_host_main`) VALUES ('%s', 0, 0, 0)" % (host, )
		dbm.query( sql )
		id_host = dbm.lastrowid
	return id_host
	
def getIdByURL( url ):
	#print "getIdByURL: %s" % url
	
	# TODO: solucionar URL's con Ñ
	try:
		urlhash = hashlib.sha1(url).hexdigest()
		_id = getIdByHash( urlhash )
		if _id is None:
			# obtenemos id de host
			o = urlparse( url )
			id_host = getHostIdByHost( o.hostname )
			# creamos enlace
			_url = url.replace("'", "\\'")
			sql = "INSERT INTO as_pages (`hash`, `url`, `id_host`, `id_contenttype`, `id_charset`, `time_fetch`, `value`) VALUES ('%s', '%s', %d, 0, 0, 0, 0)" % (urlhash, _url, id_host, )
			dbm.query( sql )
			_id = dbm.lastrowid
			# creamos entrada en caché
			cache.create( _id )
		
		return _id
	except UnicodeEncodeError:
		log.add('UnicodeEncodeError: getIdByURL: url = %s' % url)
		return 0
	
	
def update( _id, id_contenttype, id_charset, elapsed ):
	sql = "UPDATE `as_pages` SET `id_contenttype` = '%d', `id_charset` = '%d', `time_fetch` = '%s' WHERE `id` = %d; " % (id_contenttype, id_charset, elapsed, _id )
	dbm.query( sql )
	

if __name__ == '__main__':
	None

