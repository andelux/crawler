#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb

import api.log

logquery = api.log.Logger('sql.log', 'query')

class Db():
	db = None
	cursor = None
	lastrowid = None
	access = None
	
	def __init__(self, dbhost, dbuser, dbpass, dbname):
		self.access = [dbhost, dbuser, dbpass, dbname]
		self.db = MySQLdb.connect(host=dbhost, user=dbuser,passwd=dbpass,db=dbname)
		self.db.autocommit( True )

	def _query(self, sql):
		if sql is None:
			return None

		try:
			logquery.add(sql)
		except:
			pass
		
		self.cursor = self.db.cursor()
		self.cursor.execute( sql )
		return self.cursor
		
	def query(self, sql):
		self._query( sql )
		self.lastrowid = self.cursor.lastrowid
		self.cursor.close()
		#self.db.commit()
		
	def fetchAll(self, sql = None):
		self._query( sql )
		data = self.cursor.fetchall()
		self.cursor.close()
		return data

	def fetch(self, sql = None):
		self._query( sql )
		data = self.cursor.fetchone()
		self.cursor.close()
		return data

	def fetchValue(self, sql = None):
		self._query( sql )
		data = self.cursor.fetchone()
		self.cursor.close()
		if data is None:
			return None
		else:
			return data[0]
		
