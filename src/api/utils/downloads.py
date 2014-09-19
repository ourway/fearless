#!/usr/bin/env python
# -*- coding: utf-8 -*-
_author = 'Farsheed Ashouri'
'''
   ___              _                   _ 
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an appology! 
Clean code is much better than Cleaner comments!
'''


import falcon
import ujson
import uwsgi
from model import getdb
from tasks import download
from opensource.contenttype import contenttype
db=getdb()

def clean(req, resp, *kw):
    #print kw
    #print dir(db)
    db.commit()
    #db.close()


class Downloads(object):
    @falcon.after(clean)
    def on_put(self, req, resp, **kw):
        '''Register a departement'''
        url = req.get_param('url')
        if url:
            download.delay(url)


    @falcon.after(clean)
    def on_delete(self, req, resp, **kw):
        '''delete a departement'''
        pass


