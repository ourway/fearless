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
import os
from model import getdb
from tasks import add_asset
from tasks import remove_asset
import base64
import hashlib
from opensource.contenttype import contenttype
from model import file_bucket  ## riak bucket for our files
from riak import RiakObject  ## riak bucket for our files

class Assets(object):
    #@falcon.after(clean)
    def on_put(self, req, resp, **kw):
        '''Register an asset'''
        b64 = req.get_param('b64')
        path = req.get_param('path')

        if path:  #NOTE overwrites b64 param
            with open(path, 'rb') as f:
                b64 = base64.encodestring(f.read())

        name = '{path}@{md5}'.format(path=path,
                    md5=hashlib.md5(b64).hexdigest())
        add_asset.delay(name, b64)
        data = {'message':'OK', 'info':'file {name} queued.'.format(name=name)}
        resp.body = ujson.dumps(data)


    #@falcon.after(clean)
    def on_delete(self, req, resp, **kw):
        '''delete an asset'''
        name = req.get_param('name')
        if name:
            remove_asset.delay(name)
 
    def on_get(self, req, resp, **kw):
        '''delete a departement'''
        path = req.get_param('path')
        if path:
            fpath, md5 = path.split('@')
            asset = file_bucket.get(path).data
            if asset:
                resp.content_type = contenttype(fpath)
                basename = os.path.basename(fpath)
                resp.set_header('Content-Disposition', 
                        '''Attachment; filename*= UTF-8''{basename}'''.format(basename=basename))
                resp.body = base64.decodestring(asset.get('base64'))
            else:
        
                resp.status = falcon.HTTP_404
                resp.body = 'File Not Available'
        else:
            resp.status = falcon.HTTP_400
