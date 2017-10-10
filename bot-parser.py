#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import hashlib

from andelux.path import PATHS
PATHS['ROOT'] = os.path.realpath('.')
import andelux.api.cache
import andelux.api.page
import andelux.api.log
from andelux.parser import parser


# LOG OBJECT
log = andelux.api.log.Logger("andelux.log", "parser")


pages = andelux.api.cache.getNext( 50, 'cached' )

print "PARSER: %d new parsable pages" % len(pages)

for page in pages:
	url = page['url']
	urlhash = page['hash']
	if urlhash is None or urlhash.strip() == '':
		urlhash = hashlib.sha1(url).hexdigest()
		
	#print "parsgin %s" % url
	parser(page['id'], url, urlhash)
		
	#print page


