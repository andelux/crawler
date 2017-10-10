#!/usr/bin/env python
# -*- coding: utf-8 -*-

#if __name__ == "__main__" and __package__ is None:
#	__package__ = "andelux.api.cache"
    
from .. import db
import page

dbm = db.Db('localhost', 'andeluxsearch', 'andeluxsearch', 'andeluxsearch')

def getNext( limit, status = None, ids = None ):

	date_sql = 'as_pages_cache.date_next <= NOW()'
	order_sql = 'as_pages_cache.date_next'
	status_sql = ''
	ids_sql = ''
	
	if not status is None:
		date_sql = 'as_pages_cache.date <= NOW()'
		order_sql = 'as_pages_cache.date'
		status_sql = "AND as_pages_cache.status = '%s'" % status 

	if not ids is None:
		for i in range(len(ids)):
			ids[i] = str(ids[i])
		ids_sql = "AND as_pages.`id` IN (%s)" % ','.join(ids)

	sql = """
		SELECT
			as_pages.*
		FROM as_pages
		JOIN as_pages_cache ON (as_pages_cache.id_page = as_pages.id)
		WHERE %s
		%s
		%s
		ORDER BY %s ASC
		LIMIT %d
	""" % (date_sql, status_sql, ids_sql, order_sql, limit, )
	
	rows = []
	for row in dbm.fetchAll( sql ):
		data = {}
		data['id'] = row[0]
		data['hash'] = row[1]
		data['url'] = row[2]
		data['id_host'] = row[3]
		data['id_contenttype'] = row[4]
		data['id_charset'] = row[5]
		data['time_fetch'] = row[6]
		data['value'] = row[7]
		rows.append( data )

	return rows	


def getCache(_id):
	sql = "SELECT * FROM as_pages_cache WHERE `id_page` = %d LIMIT 1" % _id
	
	r = dbm.fetch( sql )
	if r is None: return None
	row = {}
	row['id_page'] = r[0]
	row['date'] = r[1]
	row['date_next'] = r[2]
	row['frecuency'] = r[3]
	row['status'] = r[4]
	return row

def create( id_page ):
	frecuency = '1 DAY'
	sql = "INSERT INTO as_pages_cache (`id_page`, `date`, `date_next`, `frecuency`, `status`) VALUES (%d, NOW(), NOW(), '%s', 'new')" % (id_page, frecuency, )
	dbm.query( sql )


def update(_id, data):

	(code, contenttype, charset, elapsed, diff) = data
	
	if code == 200:

		# obtenemos id de content-type y charset
		id_contenttype = page.getIdContenttype( contenttype )
		id_charset = page.getIdCharset( charset )

		# actualizamos datos de página
		page.update( _id, id_contenttype, id_charset, elapsed )
	
		# obtenemos la nueva fecha en la que pasará el fetcher, usando la variable
		#	'diff', que es el porcentaje que ha cambiado la página desde la última 
		#	vez que se visitó
		cache = getCache( _id )
		frecuency = cache['frecuency']
	
		if diff < 1:
			# demasiados pocos cambios, incrementamos la frecuencia en la que pasar
			if frecuency == '1 HOUR':
				frecuency = '2 HOUR'
			elif frecuency == '2 HOUR':
				frecuency = '4 HOUR'
			elif frecuency == '4 HOUR':
				frecuency = '8 HOUR'
			elif frecuency == '8 HOUR':
				frecuency = '16 HOUR'
			elif frecuency == '16 HOUR':
				frecuency = '1 DAY'
			elif frecuency == '1 DAY':
				frecuency = '2 DAY'
			elif frecuency == '2 DAY':
				frecuency = '4 DAY'
			elif frecuency == '4 DAY':
				frecuency = '1 WEEK'
			elif frecuency == '1 WEEK':
				frecuency = '2 WEEK'
			elif frecuency == '2 WEEK':
				frecuency = '1 MONTH'
			elif frecuency == '1 MONTH':
				frecuency = '2 MONTH'
			elif frecuency == '2 MONTH':
				frecuency = '4 MONTH'
			else:
				frecuency = '6 MONTH'
		
		# marcamos el estado de la cache como "cached"
		# guardamos fecha actual y fecha de próxima visita
		# actualizamos frecuencia de paso
		sql = "UPDATE as_pages_cache SET date = NOW(), date_next = DATE_ADD(NOW(), INTERVAL %s), frecuency = '%s', status = 'cached' WHERE id_page = %d" % (frecuency, frecuency, _id)
		dbm.query( sql )
		
	elif code == 301:
		None
		
	elif code == 302:
		None
		
	elif code == 404:
		None
	
def setStatus(id_page, status):
	sql = "UPDATE as_pages_cache SET status = '%s' WHERE id_page = %d" % (status, id_page)
	dbm.query( sql )

	
if __name__ == '__main__':
	None

