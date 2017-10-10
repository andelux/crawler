#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import hashlib

from andelux.path import PATHS
PATHS['ROOT'] = os.path.realpath('.')
import andelux.api.cache
import andelux.api.log
import andelux.api.page
from andelux.fetcher import fetcher


# LOG OBJECT
log = andelux.api.log.Logger("andelux.log", "fetcher")


if __name__ == '__main__':
	if len(sys.argv) > 1:
		url = sys.argv[1]

		id_page = andelux.api.page.getIdByURL( url )

		pages = andelux.api.cache.getNext( 1, 'new', [id_page] )
	else:
		pages = andelux.api.cache.getNext( 50 )
		
	for page in pages:
		url = page['url']
		urlhash = page['hash']
		if urlhash is None or urlhash.strip() == '':
			urlhash = hashlib.sha1(url).hexdigest()
		data = fetcher(url, urlhash)

		#print data

		if data[0] == 200:
			andelux.api.cache.update( page['id'], data )
		
		print data


