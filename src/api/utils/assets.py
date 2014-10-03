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


import bottle
import ujson
import sys, time
from os import path
from model import getdb
from tasks import add_asset
from tasks import remove_asset
from tasks import show_secrets
from tasks import STORAGE
from utils.fagit import GIT
from utils.validators import checkPath
#from celery.result import AsyncResult

import base64
import hashlib
from opensource.contenttype import contenttype
from model import file_bucket  ## riak bucket for our files
from riak import RiakObject  ## riak bucket for our files


asset_api = bottle.Bottle()

def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]

'''
This is a funtion that lets api to get a big/small file from user.

'''


@asset_api.post('/save/<user>/<repo>')
@asset_api.post('/save/<user>/<repo>/')
def addNewAsset(user, repo):
    '''Get data based on a file object or b64 data, save and commit it'''
    uploadByFileMethod = bottle.request.files.get('asset')
    if uploadByFileMethod:
        targetNewFilePath = path.abspath(path.join(STORAGE,
                        user, repo, uploadByFileMethod.filename))
        checkPath(path.dirname(targetNewFilePath))
        uploadByFileMethod.save(targetNewFilePath, overwrite=True) # appends upload.filename automatically
        newAsset = add_asset.delay(user, repo, uploadedFilePath=targetNewFilePath)
        return '<a href="/asset/get/{id}">Click to download</a>'.format(id=newAsset.task_id)


@asset_api.get('/get/<key>')
def serveAsset(key):
    '''Serve asset based on a key (riak key for finding path'''
    assetRiakObject = file_bucket.get(key)  ## key is the task_id! :)
    if assetRiakObject.exists:
        bottle.response.content_type = 'application/json'
        assetInfo = ujson.loads(assetRiakObject.data)
        bottle.response.add_header('Expires', 'Thu, 01 Dec 1994 16:00:00 GMT')
        noDownloadDialogFormats = ['m4v', 'jpg', 'png', 'gif', 'txt']
        downloadDialogFileName = None
        if not assetInfo.get('ext').lower() in noDownloadDialogFormats:
            downloadDialogFileName = assetInfo.get('originalName')
        return bottle.static_file(assetInfo.get('path'),
                root='/', download= downloadDialogFileName)
    else:
        taskResult = add_asset.AsyncResult(key)
        bottle.response.status = '404 Not Found'
        return taskResult.status
