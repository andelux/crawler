#!/usr/bin/env python
# -*- coding: utf-8 -*-

#if __name__ == "__main__" and __package__ is None:
#	__package__ = "andelux.api.link"
    
from .. import db

dbm = db.Db('localhost', 'andeluxsearch', 'andeluxsearch', 'andeluxsearch')

def exists( id_page, id_page_link ):
	sql = "SELECT COUNT(*) FROM as_pages_links WHERE id_page = %d AND id_page_link = %d LIMIT 1" % (id_page, id_page_link, )
	count = int( dbm.fetchValue( sql ) )
	if count > 0: return True
	return False
	
def setLink( id_page, id_page_link, where, anchor = '' ):
	if not exists(id_page, id_page_link):
		if anchor is None: anchor = ''
		sql = "INSERT INTO as_pages_links (`id_page`, `id_page_link`, `value`, `where`, `anchor`) VALUES (%d, %d, %d, '%s', '%s')" % (id_page, id_page_link, 0, where, anchor)
		dbm.query( sql )

if __name__ == '__main__':
	None

