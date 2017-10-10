#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from ..path import PATHS
from time import gmtime, strftime


class Logger():
	logsdir = PATHS['ROOT'] + '/log/'
	prefix = 'log'
	filename = ''
	
	def __init__(self, filename, prefix):
		self.prefix = prefix
		self.filename = self.logsdir + filename
		try:
			#print self.logsdir
			os.makedirs( self.logsdir )
		except OSError:
			None

		try:
			self.f = open( self.filename, 'a')			
		except IOError:
			print "FATAL ERROR: unable to open log file: %s\n" % (self.logsdir + '/' + filename)
			sys.exit()
			
	def add(self, text):
		self.f.write('[%s] %s - %s\n' % (self.prefix, strftime("%a %d %b %Y %H:%M:%S %Z", gmtime()), text))

logger = Logger("andelux.log", "-")

def add( text ):
	logger.add( text )
	
if __name__ == '__main__':
	add( 'probando' )
