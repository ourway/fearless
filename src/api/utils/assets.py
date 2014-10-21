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
from cStringIO import StringIO
import falcon
import os
from helpers import commit
from sys import stderr
from os import path
from tasks import add_asset
from tasks import STORAGE
from opensource.contenttype import contenttype
from utils.validators import checkPath
from base64 import encode

# from celery.result import AsyncResult
from models import Asset, Repository, es, session




def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]


'''
This is a funtion that lets api to get a big/small file from user.

'''

#@asset_api.post('/save/<user>/<repo>')


class AssetSave:

    @falcon.after(commit)
    def on_put(self, req, resp, repo):
        '''Get data based on a file object or b64 data, save and commit it'''
        targetRepo = session.query(Repository).filter(Repository.name==repo).first()
        body = req.stream
        if targetRepo:
            name = req.get_param('name') or 'undefined.%s.raw'%_generate_id()
            tempraryStoragePath = path.join(targetRepo.path,
                contenttype(name).split(';')[0].replace('x-', ''), name)
            bodyMd5 = safeCopyAndMd5(body, tempraryStoragePath)
            old_asset = session.query(Asset).filter(Asset.repository==targetRepo).filter(Asset.key==bodyMd5).first()
            if not old_asset:
                asset = Asset(key=bodyMd5, repository=targetRepo)
                session.add(asset)
                newAsset = add_asset.delay(bodyMd5, tempraryStoragePath)
                asset.task_id = newAsset.task_id
                resp.body = {'message':'Asset created', 'key': asset.key}
                #resp.body = "I am working"
            else:
                resp.body = {'message':'Asset already available'}
        else:
            while True:
                chunk = req.stream.read(2**20)
                if not chunk: break

            resp.body = {'message':'Repo is not available'}


def safeCopyAndMd5(fileobj, destinationPath):
    '''copy a file in chunked mode safely'''

    destDir = path.dirname(destinationPath)
    ext = destinationPath.split('.')[-1]
    checkPath(destDir)
    if path.isfile(destinationPath):
        os.remove(destinationPath)
    f = open(destinationPath, 'wb')
    md5 = hashlib.md5()
    while True:
        chunk = fileobj.read(2 ** 20)
        if not chunk:
            break
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
    if not '-' in key:  # it might not be a MD5!! Lets find:
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

        raw = es.search(
            index='assets2', doc_type='info', body=queryDSL).get('hits')
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
                if keydata:  # if key is there
                    assetInfo[key] = keydata[0]

    return assetInfo


class GetAsset:

    def on_get(self, req, resp, key):
        '''Serve asset based on a key (riak key for finding path'''

        target = session.query(Asset).filter(Asset.key==key).first()
        if target:
            print target
            filepath = os.path.join(target.repository.path, target.path)
            f = open(filepath)
            #resp.stream_len=500
            if req.get_param('b64'):
                encf = StringIO()
                encode(f, encf)
                encf.seek(0, os.SEEK_END)
                datalen = s.tell()
                encf.seek(0)
                resp.stream_len = datalen
                resp.stream = encf
            else:
                resp.content_type = str(target.content_type)
                resp.stream_len = os.path.getsize(filepath)
                resp.stream = f

class ListAssets:

    def on_get(self, req, resp):
        page = req.get_param('page') or 1
        userName = req.get_param('user') or '*'
        repositoryName = req.get_param('repo') or '*'
        content_type = req.get_param('type') or '*'
        originalName = req.get_param('name') or '*'
        extension = req.get_param('ext') or '*'

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
        raw = es.search(
            index='assets', doc_type='info', body=queryDSL).get('hits')
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
                if keydata:  # if key is there
                    assetExtractedData[key] = keydata[0]
            results.append(assetExtractedData)
        resp.body = results
