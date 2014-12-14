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
from urllib import unquote
import os
import cgi
from helpers import commit, get_params
from sys import stderr
from os import path
from tasks import add_asset
from tasks import STORAGE
from opensource.contenttype import contenttype
from utils.validators import checkPath
from base64 import encode, decode, decodestring

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

        targetUser = session.query(User).filter(User.alias == uploader).first()
        
        if not targetRepo:
            pr = session.query(Repository).filter(Repository.name == repo).first()
            if not pr:
                targetRepo = Repository(name=repo,
                                        path=os.path.join(public_repository_path, repo))
                session.add(targetRepo)
            else:
                targetRepo = pr

        _cid = req.get_param('collection_id')
        if _cid:
            collection = session.query(Collection).filter_by(repository=targetRepo)\
                            .filter_by(id=_cid).first()
        _cname = req.get_param('collection')
        if _cname:
            collection = session.query(Collection).filter_by(repository=targetRepo)\
                            .filter_by(name=_cname).first()
        if not collection:
            collection = Collection(path='danger', repository=targetRepo)
            session.add(collection)


        
        body = req.stream

        b64 = req.get_param('b64')
        mt = req.get_param('multipart')
        mtname = None
        if mt:
            fs = cgi.FieldStorage(fp=req.stream, environ=req.env)
            body = fs['file'].file
            mtname = fs['file'].filename


        thumbnail = req.get_param('thmb')
        attach_to = req.get_param('attach_to')
        if targetRepo and body:
            if not mtname:
                name = req.get_param('name') or 'undefined.%s.raw' % _generate_id()
            else:
                name = mtname
            assetExt = name.split('.')[-1]
            content_type = contenttype(name)
            assetPath = name
            tempraryStoragePath = path.join(targetRepo.path, collection.path,
                                            name)

            name, bodyMd5 = safeCopyAndMd5(body, tempraryStoragePath, b64=b64)
            asset = session.query(Asset).filter(
                Asset.repository == targetRepo).filter_by(collection=collection)\
                        .filter_by(key=bodyMd5).first()
            if not asset:
                asset = Asset(key=bodyMd5, repository=targetRepo,
                              collection=collection, name=name[-20:].replace('_', ' '), fullname=name,
                              path=assetPath, ext=assetExt, owner=targetUser)
                session.add(asset)
            else:
                asset.version += 1

            # Asset descriptions
            if req.get_param('description'):
                asset.description = req.get_param('description')
            
            asset.name = name[-20:].replace('_', ' ')
            asset.fullname = name

            asset.key = bodyMd5
            if targetUser:
                asset.modifiers.append(targetUser)
                asset.users.append(targetUser)
            if thumbnail:
                thumbnail = unquote(thumbnail)
                asset.thumbnail = thumbnail 


            if attach_to:
                parent_id = int(attach_to)
                parent = session.query(Asset).filter(Asset.id == parent_id).first()
                asset.attached_to.append(parent)


                
                #newAsset = add_asset.delay(bodyMd5, tempraryStoragePath)
                #asset.task_id = newAsset.task_id
            resp.body = {'message': 'Asset created|updated', 'key': asset.key,
                         'url': asset.url, 'fullname':asset.fullname,
                         'name':asset.name, 'content_type':asset.content_type.split('/')[0]}
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
        basename = 'C.' + basename
        destinationPath = os.path.join(destDir, basename)
        #os.remove(destinationPath)
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
            attachments = [{'name':i.name, 'url':i.url, 
                            'description':i.description, 
                            'thumbnail':i.thumbnail, 'content_type':i.content_type} for i in target.attachments]
            resp.body = {'url':os.path.join('/static', target.url),
                         'size':sz, 'key':target.key, 'id':target.id,
                         'version':target.version, 'datetime':target.modified_on,
                         'last_updated_by':modifier.alias, 'descripion':target.description,
                         'owner':target.owner.alias, 'thumbnail':target.thumbnail, 
                         'attachments':attachments}


class DeleteAsset:
    @falcon.after(commit)
    def on_delete(self, req, resp, id):
        target = session.query(Asset).filter(Asset.id == id).first()
        userInfo = getUserInfoFromSession(req)
        if userInfo.get('id') == target.owner.id:
            session.delete(target)
            resp.status = falcon.HTTP_202

        


        
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


class CollectionInfo:
    def on_get(self, req, resp, collectionId):
        target = session.query(Collection).filter(Collection.id==int(collectionId)).first()
        if target:
            assets = session.query(Asset).filter_by(collection=target).all()
            data = dict()
            data['name'] = target.name
            data['assets'] = [{'id':i.id, 'name':i.name, 'url':i.url, 'fullname':i.fullname, 
                               'description':i.description, 'content_type':i.content_type.split('/')[0]} for i in assets]
            data['id'] = target.id
            data['container'] = target.container
            data['holdAssets'] = target.holdAssets
            data['path'] = target.path
            data['description'] = target.description
            data['repository'] = {'name':target.repository.name, 'id':target.repository.id}
            data['project'] = {'name':target.repository.project.name, 'id':target.repository.project.id}
            _t = target.parent
            d = data
            while True:
                if _t:
                    d['parent'] = {'name':_t.name, 'id':_t.id, 'path':_t.path}
                    d = d['parent']
                    _t = _t.parent
                else:
                    break
            if target.children:
                data['children'] = [{'name':i.name, 'id':i.id, 'path':i.path,
                                     'children':[{'name':c1.name, 'id':c1.id, 'path':c1.path, } for c1 in i.children]
                                     } for i in target.children]
            resp.body = data

class AddCollection:
    @falcon.after(commit)
    def on_put(self, req, resp):
        data = get_params(req.stream, flat=False)
        name = data.get('name')
        repository_id = data.get('repository_id')
        parent_id = data.get('parent_id')

        template = data.get('template').lower()
        if name and repository_id:
            newC = Collection(name=name, path=name, repository_id=repository_id)
            if parent_id:
                newC.parent_id = parent_id
            if template:
                newC.template = template

            if not os.path.isdir(newC.url):
                session.add(newC)
                resp.body = {'message':'OK', 'info':'Collection created'}
            else:
                resp.body = {'message':'ERROR', 'info':'Collection is available on server'}
        
        


        
