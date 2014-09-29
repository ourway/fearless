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
import os, sys, time
from model import getdb
from tasks import add_asset
from tasks import remove_asset
from tasks import STORAGE
from utils.fagit import GIT
#from celery.result import AsyncResult

import base64
import hashlib
from opensource.contenttype import contenttype
from model import file_bucket  ## riak bucket for our files
from riak import RiakObject  ## riak bucket for our files


def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]

class Assets(object):
    #@falcon.after(clean)
    def on_put(self, req, resp, user, reponame,  **kw):
        '''Register an asset'''

        b64 = req.get_param('b64')
        path = req.get_param('path')
        if path or b64:
            x = add_asset.delay(user, reponame, b64=b64, path=path)

            data = {'message':'OK', 'info':'file queued.', 
                    'task_id':x.task_id}
            resp.body = ujson.dumps(data)
            return
        else:
            resp.status = falcon.HTTP_400
            data = {'message':'ERROR', 'info':'path or b64 parameter not found!'}
            resp.body = ujson.dumps(data)

    #@falcon.after(clean)
    def on_delete(self, req, resp, **kw):
        '''delete an asset'''
        name = req.get_param('name')
        if name:
            remove_asset.delay(name)
 
    def on_get(self, req, resp, **kw):
        '''delete a departement'''
        id = req.get_param('id')
        info = req.get_param('info')
        key = req.get_param('key')

        if id and key:
            resp.status = falcon.HTTP_400
            resp.body=ujson.dumps({'message':'ERROR', 
                'info':'key and is conflict.  Use only one of them!'})
            return

        elif not (id or key):
            resp.status = falcon.HTTP_400
            resp.body=ujson.dumps({'message':'ERROR', 
                'info':'key or id missing!'})
            return


        elif id:
            result = add_asset.AsyncResult(id)
            if result.successful():
                key = result.get()
                ############## Get key info ##############
                if info:
                    resp.body=ujson.dumps({'message':'OK', 
                        'key':key})
                    return
            else:
                data = {'message':result.status}
                resp.body = ujson.dumps(data)
                return

                
        resp.content_type = contenttype(key)
        resp.status = falcon.HTTP_307
        fileinfo = file_bucket.get(key)
        info = ujson.loads(fileinfo.data)
        file_user = info.get('user')
        file_repo = info.get('repo')
        file_path = os.path.join(STORAGE, file_user, file_repo, key)
        location = '/static/{u}/{r}/{path}'.format(path=key,
                        u=file_user, r=file_repo)
        print file_path
        if not os.path.isfile(file_path):
            print 'recovering asset ...'
            repo = GIT(file_path)
            repo.recover()
        
        #resp.set_header('Access-Control-Allow-Origin', '*')
        resp.location = location
#            asset = file_bucket.get(key)
#            if asset.exists: ## Aset is available
#                data = ujson.loads(asset.data)
#                b64 = data.get('base64')
#                ext = data.get('ext')
#                x = add_asset.delay(b64=b64, ext=ext)
#                x.wait()
#                location = '/api/asset?id={id}&v={rnd}'.format(id=id, rnd=_generate_id())
#                resp.location = location
#
#            else:
#                resp.status = falcon.HTTP_404
#                return

