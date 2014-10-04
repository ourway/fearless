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

import ujson
import time
import hashlib
import falcon
import bottle
import os
from sys import stderr
from os import path
from tasks import add_asset
from tasks import STORAGE
from utils.validators import checkPath
import multipart ##git@github.com:hydrogen18/multipart-python.git

# from celery.result import AsyncResult

from model import file_bucket, ES  ## riak bucket for our files


asset_api = bottle.Bottle()


def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]


'''
This is a funtion that lets api to get a big/small file from user.

'''

#@asset_api.post('/save/<user>/<repo>')
class AssetSave:
    def on_post(self, req, resp, user, repo):
        '''Get data based on a file object or b64 data, save and commit it'''
        contentType = req.content_type
        #print req.stream.read()
        magic = 'boundary='
        offset = contentType.index(magic)
        assets = {}
        boundary = '--' + contentType[offset + len(magic):]
        for headers, data in multipart.Parser(boundary, req.stream):
            originalName = headers.next()[1].split(';')[-1].split('=')[-1][1:-1]
            if originalName:
                tempraryStoragePath = path.join(STORAGE, user, repo, originalName)
                bodyMd5 = safeCopyAndMd5(data, tempraryStoragePath,
                            isGenerator=True)
                newAsset = add_asset.delay(user, repo,
                        uploadedFilePath=tempraryStoragePath, dataMD5=bodyMd5)
                assets[originalName] = newAsset.task_id
        resp.body = ujson.dumps(assets)


    def on_put(self, req, resp, user, repo):
        '''Get data based on a file object or b64 data, save and commit it'''
        print '\nI got request\n'
        name = req.get_param('name') or 'undefined.data'
        tempraryStoragePath = path.join(STORAGE, user, repo, name)
        body = req.stream
        bodyMd5 = safeCopyAndMd5(body, tempraryStoragePath)
        newAsset = add_asset.delay(user, repo, uploadedFilePath=tempraryStoragePath, dataMD5=bodyMd5)
        resp.body = newAsset.task_id
        #resp.body = "I am working"

def safeCopyAndMd5(fileobj, destinationPath, isGenerator=False):
    '''copy a file in chunked mode safely'''
    destDir = path.dirname(destinationPath)
    ext = destinationPath.split('.')[-1]
    checkPath(destDir)
    if path.isfile(destinationPath):
        os.remove(destinationPath)
    f = open(destinationPath, 'wb')
    md5 = hashlib.md5()
    if not isGenerator:
        while True:
            chunk = fileobj.read(2**16)
            if not chunk:
                break
            md5.update(chunk)
            f.write(chunk)
    else:
        for chunk in fileobj:
            md5.update(chunk)
            f.write(chunk)
    f.close()
    dataMd5 = md5.hexdigest()
    newAssetName = '%s.%s' % (dataMd5, ext)
    finalStoragePath = path.join(destDir, newAssetName)
    if not path.isfile(finalStoragePath):
        os.rename(destinationPath, finalStoragePath)
    else:
        os.remove(destinationPath)
    os.symlink(newAssetName, destinationPath)
    return dataMd5




def getAssetInfo(key):
    '''Get asset Info based on key or md5'''

    assetInfo = None
    if not '-' in key:  ## it might not be a MD5!! Lets find:
        queryDSL = {
            "fields": ['path', 'ext', 'originalName',
                       'content_type', 'repo', 'user', 'md5'],
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
            assetContentType = assetHitInfo['fields'].get('cont')
            assetOwner = assetHitInfo['fields'].get('user')
            assetRepositoryName = assetHitInfo['fields'].get('repo')
            assetMd5 = assetHitInfo['fields'].get('md5')

            assetInfo = {
                'originalName': assetOriginalName,
                'path': assetFilePath,
                'ext': assetFileExtension,
                'content_type': assetContentType,
                'user': assetOwner,
                'repo': assetRepositoryName,
                'md5': assetMd5
            }

            for key in assetInfo:
                keydata = assetInfo.get(key)
                if keydata:  ## if key is there
                    assetInfo[key] = keydata[0]
    else:
        assetRiakObject = file_bucket.get(key)  ## key is the task_id! :)
        if assetRiakObject.exists:
            assetInfo = ujson.loads(assetRiakObject.data)
    return assetInfo


@asset_api.get('/get/<key>')
def serveAsset(key):
    '''Serve asset based on a key (riak key for finding path'''
    assetInfo = getAssetInfo(key)
    if assetInfo:
        noDownloadDialogFormats = ['m4v', 'mp4', 'json',
                                   'pdf', 'svg', 'jpg', 'png', 'gif', 'txt']
        downloadDialogFileName = None
        staticFilePath = assetInfo.get('path')
        if not assetInfo.get('ext').lower() in noDownloadDialogFormats:
            downloadDialogFileName = assetInfo.get('originalName')
        bottle.response.content_type = assetInfo.get('content_type')
        assetStatisPath = '{user}/{repo}/{md5}.{ext}'.format(
            user=assetInfo.get('user'),
            repo=assetInfo.get('repo'),
            md5=assetInfo.get('md5'),
            ext=assetInfo.get('ext'),
        )
        assetStaticUrl = '/static/%s' % assetStatisPath
        bottle.redirect(assetStaticUrl)
        #return bottle.static_file(staticFilePath,
        #                          root='/', download=downloadDialogFileName)
    else:
        taskResult = add_asset.AsyncResult(key)
        bottle.response.status = '404 Not Found'
        return taskResult.status


def fileGenerator(staticFilePath):
    with open(staticFilePath, 'rb') as targetStaticFile:
        while True:
            chunk = targetStaticFile.read(2 ** 20)
            if not chunk:
                break
            yield chunk


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
        "from": (page - 1) * limit,
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
            if keydata:  ## if key is there
                assetExtractedData[key] = keydata[0]
        results.append(assetExtractedData)

    bottle.response.content_type = 'application/json'
    return ujson.dumps(results)

