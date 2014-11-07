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
from base64 import encode, decode

# from celery.result import AsyncResult
from models import Asset, Repository, Collection, es, session, User
from AAA import getUserInfoFromSession
from defaults import public_repository_path
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
        userInfo = getUserInfoFromSession(req)
        uploader = userInfo.get('alias')

        targetRepo = session.query(Repository).filter(
            Repository.name == repo).first()

        if not uploader:
            uploader = 'anonymous'
            targetRepo = session.query(Repository).filter(Repository.name == 'public').first()

        if not targetRepo:
            pr = session.query(Repository).filter(Repository.name == repo).first()
            if not pr:
                targetRepo = Repository(name=repo,
                                        path=os.path.join(public_repository_path, repo))
                session.add(targetRepo)
            else:
                targetRepo = pr

        _collection = req.get_param('collection')

        if not _collection:
            _collection = 'danger'
        collection = session.query(Collection).filter(Collection.repository==targetRepo)\
                        .filter(Collection.path==_collection).first()
        if not collection:
            collection = Collection(path=_collection, repository=targetRepo)
            session.add(collection)


        body = req.stream
        b64 = req.get_param('b64')
        if targetRepo and body:
            name = req.get_param('name') or 'undefined.%s.raw' % _generate_id()
            assetExt = name.split('.')[-1]
            assetPath = contenttype(name).split(';')[0].replace('x-', '') or ''
            tempraryStoragePath = path.join(targetRepo.path, collection.path,
                                            assetPath, name)

            name, bodyMd5 = safeCopyAndMd5(body, tempraryStoragePath, b64=b64)
            asset = session.query(Asset).filter(
                Asset.repository == targetRepo).filter(Asset.collection == collection)\
                        .filter(Asset.name==name).first()
            if not asset:
                asset = Asset(key=bodyMd5, repository=targetRepo,
                              collection=collection, name=name,
                              path=assetPath, ext=assetExt)
                session.add(asset)
            else:
                asset.version += 1

            # Asset descriptions
            if req.get_param('description'):
                asset.description = req.get_param('description')


            asset.key = bodyMd5
            targetUser = session.query(User).filter(User.alias == uploader).first()
            if targetUser:
                asset.modifiers.append(targetUser)
                asset.users.append(targetUser)
                #newAsset = add_asset.delay(bodyMd5, tempraryStoragePath)
                #asset.task_id = newAsset.task_id
            resp.body = {'message': 'Asset created|updated', 'key': asset.key,
                             'url': asset.url}
                #resp.body = "I am working"
        else:  ## lets consume the stream!
            while True:
                chunk = req.stream.read(2 ** 20)
                if not chunk:
                    break

            resp.body = {'message': 'Repo is not available'}


def safeCopyAndMd5(fileobj, destinationPath, b64=False):
    '''copy a file in chunked mode safely'''

    destDir = path.dirname(destinationPath)
    extsp = destinationPath.split('.')
    basename = os.path.basename(destinationPath)
    if len(extsp)>1:
        ext = extsp[1]
    else:
        ext = 'raw'
    checkPath(destDir)
    if path.isfile(destinationPath):
        os.remove(destinationPath)
    f = open(destinationPath, 'wb')
    md5 = hashlib.md5()
    if b64:
        b = StringIO()
        decode(fileobj, b)
        b.seek(0)
        fileobj = b

    while True:
        chunk = fileobj.read(2 ** 20)
        if not chunk:
            break
        md5.update(chunk)
        f.write(chunk)

    f.close()
    dataMd5 = md5.hexdigest()

    return (basename, dataMd5)


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

    def on_post(self, req, resp, key):
        '''Serve asset based on a key (riak key for finding path'''

        name = req.get_param('name')
        if name == 'true':
            target = session.query(Asset).filter(Asset.name == key).first()
        else:
            target = session.query(Asset).filter(Asset.key == key).first()
        if target:
            sz = os.path.getsize(target.full_path)
            modifier = target.modifiers[-1]
            resp.body = {'url':os.path.join('/static', target.url),
                         'size':sz, 'key':target.key,
                         'version':target.version, 'datetime':target.modified_on,
                         'last_updated_by':modifier.alias, 'descripion':target.description}



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
