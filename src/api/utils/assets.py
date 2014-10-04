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
from model import file_bucket, ES  ## riak bucket for our files
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
    assetsList = list()
    for key in bottle.request.files.keys():
        uploadByFileMethod = bottle.request.files.get(key)
        targetNewFilePath = path.abspath(path.join(STORAGE,
                        user, repo, uploadByFileMethod.filename))
        checkPath(path.dirname(targetNewFilePath))
        uploadByFileMethod.save(targetNewFilePath, overwrite=True) # appends upload.filename automatically
        newAsset = add_asset.delay(user, repo, uploadedFilePath=targetNewFilePath)
        assetsList.append(newAsset.task_id)
        yield '<a href="/asset/get/{id}">Click to download</a><br/>'.format(id=newAsset.task_id)


@asset_api.get('/get/<key>')
def serveAsset(key):
    '''Serve asset based on a key (riak key for finding path'''

    assetInfo = None
    if not '-' in key:  ## it might not be a MD5!! Lets find:
        queryDSL = {
            "fields": ['path', 'ext', 'originalName'],
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": "md5:%s" % key
                            }
                        }
                    ]
                }
            }
        }

        raw = ES.search(index='assets', doc_type='info', body=queryDSL).get('hits')
        assetInfos = raw.get('hits')
        for assetHitInfo in assetInfos:
            assetOriginalName = assetHitInfo['fields'].get('originalName')
            assetFilePath = assetHitInfo['fields'].get('path')
            assetFileExtension = assetHitInfo['fields'].get('ext')

            assetInfo = {
                'originalName': assetOriginalName,
                'path': assetFilePath,
                'ext': assetFileExtension
            }

            for key in assetInfo:
                keydata = assetInfo.get(key)
                if keydata: ## if key is there
                    assetInfo[key] = keydata[0]

    else:
        assetRiakObject = file_bucket.get(key)  ## key is the task_id! :)
        if assetRiakObject.exists:
            assetInfo = ujson.loads(assetRiakObject.data)



    if assetInfo:
        noDownloadDialogFormats = ['m4v', 'mp4', 'json',
                'pdf', 'svg', 'jpg', 'png', 'gif', 'txt']
        downloadDialogFileName = None
        staticFilePath = assetInfo.get('path')
        if not assetInfo.get('ext').lower() in noDownloadDialogFormats:
            downloadDialogFileName = assetInfo.get('originalName')
        return bottle.static_file(staticFilePath,
                root='/', download= downloadDialogFileName)
    else:
        taskResult = add_asset.AsyncResult(key)
        bottle.response.status = '404 Not Found'
        return taskResult.status


def fileGenerator(staticFilePath):
    with open(staticFilePath, 'rb') as targetStaticFile:
        while True:
            chunk = targetStaticFile.read(2**20)
            if not chunk:
                break
            yield chunk


@asset_api.get('/stream/<key>')
def serveAsset(key):
    '''Serve asset based on a key (riak key for finding path'''
    assetRiakObject = file_bucket.get(key)  ## key is the task_id! :)
    if assetRiakObject.exists:
        assetInfo = ujson.loads(assetRiakObject.data)
        downloadDialogFileName = None
        staticFilePath = assetInfo.get('path')
        bottle.response.add_header("Transfer-Encoding", "chunked")
        #return 'asdsa'
        return bottle.response()



@asset_api.get('/list')
def listAssets():
    params = bottle.request.params
    page = params.get('page') or 1
    userName = params.get('user') or '*'
    repositoryName = params.get('repo') or '*'
    content_type = params.get('type') or '*'
    originalName = params.get('name') or '*'
    extension = params.get('ext') or '*'

    try:
        page = int(page)
    except ValueError:
        page = 1
    limit = 20
    queryDSL = {
        "fields": ["user", "size", "originalName", "path",
                   "content_type", "key"],
        "size": limit,
        "from": (page-1)*limit,
         "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": "user:%s" % userName
                            }
                        },
                        {
                            "query_string": {
                                "query": "content_type:%s" % content_type
                            }
                        },
                        {
                            "query_string": {
                                "query": "repo:%s" % repositoryName
                            }
                        },
                        {
                            "query_string": {
                                "query": "originalName:%s" % originalName
                            }
                        },
                        {
                            "query_string": {
                                "query": "ext:%s" % extension
                            }
                        }
                    ]
                }
            }
    }
    raw = ES.search(index='assets', doc_type='info', body=queryDSL).get('hits')
    hitsCount = raw.get('total')
    hits = raw.get('hits')
    results = list()
    for assetInfo in hits:
        assetOriginalName = assetInfo['fields'].get('originalName')
        assetFilePath = assetInfo['fields'].get('path')
        assetFileSize = assetInfo['fields'].get('size')
        assetOwner = assetInfo['fields'].get('user')
        assetId = assetInfo['fields'].get('key')
        assetContentType = assetInfo['fields'].get('content_type')
        assetExtractedData = {
            'name': assetOriginalName,
            'content_type': assetContentType,
            'size': assetFileSize,
            'user': assetOwner,
            'key': assetId
        }
        for key in assetExtractedData:
            keydata = assetExtractedData.get(key)
            if keydata: ## if key is there
                assetExtractedData[key] =  keydata[0]
        results.append(assetExtractedData)

    bottle.response.content_type = 'application/json'
    return ujson.dumps(results)

