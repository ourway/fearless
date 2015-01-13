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
from slugify import slugify, slugify_filename
from urllib import unquote
import os
import cgi
import uuid
from helpers import commit, Commit, get_params
from sys import stderr
from os import path
from opensource.contenttype import contenttype
from utils.validators import checkPath
from base64 import encode, decode, decodestring
from sqlalchemy import desc

# from celery.result import AsyncResult
from models import Asset, Repository, Collection, es, User, fdb
from AAA import getUserInfoFromSession
from defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS
from models.mixin import getUUID

def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]


'''
This is a funtion that lets api to get a big/small file from user.

'''

#@asset_api.post('/save/<user>/<repo>')




class AssetSave:
    def on_put(self, req, resp, repo):
        '''Get data based on a file object or b64 data, save and commit it'''
        userInfo = getUserInfoFromSession(req, resp)
        uploader = userInfo.get('alias')
        targetRepo = req.session.query(Repository).filter(
            Repository.name == repo).first()

        if not uploader:
            uploader = 'anonymous'
            targetRepo = req.session.query(Repository).filter(Repository.name == 'public').first()

        targetUser = req.session.query(User).filter(User.alias == uploader).first()
        
        if not targetRepo:
            pr = req.session.query(Repository).filter(Repository.name == repo).first()
            if not pr:
                targetRepo = Repository(name=repo,
                                        path=os.path.join(public_repository_path, repo))
                req.session.add(targetRepo)
            else:
                targetRepo = pr

        _cid = req.get_param('collection_id')
        if _cid:
            collection = req.session.query(Collection).filter_by(repository=targetRepo)\
                            .filter_by(id=_cid).first()
        _cname = req.get_param('collection')
        if _cname:
            collection = req.session.query(Collection).filter_by(repository=targetRepo)\
                            .filter_by(name=_cname).first()
        if not collection:
            collection = Collection(path='danger', repository=targetRepo)
            req.session.add(collection)


        
        body = req.stream

        b64 = req.get_param('b64')
        thumbnail = req.get_param('thmb')
        mt = req.get_param('multipart')
        mtname = None
        if mt:
            try:
                fs = cgi.FieldStorage(fp=req.stream, environ=req.env)
            except (ValueError, IOError):
                resp.status = falcon.HTTP_400
                resp.body={'message':'error'}
                return

            body = fs['file'].file
            if fs.has_key('thumbnail'): ## thumbnails are dataURLs
                thumbnail = fs['thumbnail'].file.read()  ## thumbs are mostly small

            mtname = fs['file'].filename


        attach_to = req.get_param('attach_to')
        if targetRepo and body:
            if not mtname:
                name = req.get_param('name') or 'undefined.%s.raw' % _generate_id()
            else:
                name = mtname

            if name:
                name = slugify_filename(name)

            name = name.decode('utf-8')
            assetExt = name.split('.')[-1]
            content_type = contenttype(name)
            assetPath = name
            tempraryStoragePath = path.join(targetRepo.path, collection.path,
                                            name)

            name, bodyMd5 = safeCopyAndMd5(req, body, tempraryStoragePath, targetRepo.id, b64=b64)
            fullname = name
            name = (name[:10] + '..') if len(name) > 10 else name
            asset = req.session.query(Asset).filter(
                Asset.repository == targetRepo).filter_by(collection=collection)\
                        .filter_by(fullname=fullname).first()

            if not asset:
                _uid = getUUID()
                asset = Asset(key=bodyMd5, version=1, repository=targetRepo,uuid=_uid,
                              collection=collection, name=name, fullname=fullname,
                              path=assetPath, ext=assetExt, owner_id=targetUser.id)
                req.session.add(asset)
            else:
                if not bodyMd5 == asset.key:
                    asset.version += 1
                asset.name = name
                asset.fullname = fullname
                asset.key = bodyMd5

            # Asset descriptions

            if req.get_param('description'):
                asset.description = req.get_param('description')
            


            if targetUser:
                asset.modifiers.append(targetUser)
                asset.users.append(targetUser)
            if thumbnail:  ## thumbnail is base64 format
                fmt = 'png'
                fid = asset.uuid + '_thmb_' + str(asset.version)
                result = os.path.join('uploads', fid+'.'+fmt)
                thmbpath = os.path.join(public_upload_folder, fid+'.'+fmt)
                thmb_data = decodestring(unquote(thumbnail).split(',')[1])
                with open(thmbpath, 'wb') as f:
                    f.write(thmb_data)


            if attach_to:
                parent_id = int(attach_to)
                parent = req.session.query(Asset).filter(Asset.id == parent_id).first()
                asset.attached_to.append(parent)


                
                #newAsset = add_asset.delay(bodyMd5, tempraryStoragePath)
                #asset.task_id = newAsset.task_id
            resp.body = {'message': 'Asset created|updated', 'key': asset.key,
                         'url': asset.url, 'fullname':asset.fullname, 'id':asset.id,
                         'name':asset.name, 'content_type':asset.content_type.split('/')[0],
                         'datetime':time.time()}
                #resp.body = "I am working"
        else:  ## lets consume the stream!
            while True:
                chunk = req.stream.read(2 ** 20)
                if not chunk:
                    break

            resp.body = {'message': 'Repo is not available'}


def safeCopyAndMd5(req, fileobj, destinationPath, repoId, b64=False):
    '''copy a file in chunked mode safely'''

    destDir = path.dirname(destinationPath)
    extsp = destinationPath.split('.')
    basename = os.path.basename(destinationPath)
    if len(extsp)>1:
        ext = extsp[1]
    else:
        ext = 'raw'
    checkPath(destDir)
    #if path.isfile(destinationPath):
    #    basename = _generate_id() + '@@' + basename
    #    destinationPath = os.path.join(destDir, basename)
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
    ## check if there is an asset with same key
    if not repoId:
        availableAsset = req.session.query(Asset).filter_by(key=dataMd5).first()
    else:
        availableAsset = req.session.query(Asset).filter_by(key=dataMd5).join(Collection).filter_by(repository_id=repoId).first()
    if availableAsset and not os.path.isfile(availableAsset.full_path):
        req.session.delete(availableAsset)
    elif availableAsset:
        if os.path.isfile(availableAsset.full_path) and availableAsset.full_path!=destinationPath:
            os.remove(destinationPath) ## we dont need it anymore
            os.symlink(availableAsset.full_path, destinationPath)
            #print 'Symblink: %s generated' % destinationPath


    
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
            target = req.session.query(Asset).filter(Asset.fullname == key).first()
        else:
            target = req.session.query(Asset).filter(Asset.key == key).first()
        if target:
            sz = os.path.getsize(target.full_path)
            modifier = target.modifiers[-1]
            attachments = [
                        {
                            'name':i.name,
                            'url':i.url, 
                            'id':i.id,
                            'description':i.description, 
                            'thumbnail':i.thumbnail,
                            'content_type':i.content_type
                        }
                        for i in target.attachments]
            resp.body = {'url':os.path.join('/static', target.url),
                         'size':sz, 'key':target.key, 'id':target.id,
                         'version':target.version, 'datetime':target.modified_on,
                         'last_updated_by':modifier.alias, 'descripion':target.description,
                         'owner':target.owner.alias, 'thumbnail':target.thumbnail, 
                         'attachments':attachments}


class DeleteAsset:
    def on_delete(self, req, resp, id):
        target = req.session.query(Asset).filter(Asset.id == id).first()
        userInfo = getUserInfoFromSession(req, resp)
        if userInfo.get('id') == target.owner.id:
            req.session.delete(target)
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
        target = req.session.query(Collection).filter(Collection.id==int(collectionId)).first()
        start = req.get_param('s')
        end = req.get_param('e')
        if start: start = int(start)
        else: start = 0
        if end: end = int(end)
        if start!=None and not end:
            end = start+10

        end = max(start, end)

        if target:
            assets = req.session.query(Asset).filter_by(collection_id=target.id).order_by(desc(Asset.modified_on)).slice(start, end)
            assets_count = req.session.query(Asset).filter_by(collection_id=target.id).count()
            data = dict()
            data['name'] = target.name
            data['name'] = target.name
            data['assets_count'] = assets_count
            if assets:
                data['assets'] = [
                                    {'id':i.id, 
                                   'name':i.name,
                                   'url':i.url,
                                   'fullname':i.fullname,
                                   'version':i.version,
                                   'thumbnail':i.thumbnail,
                                   'preview':i.preview,
                                   'poster':i.poster,
                                   'owner':{
                                            'id':i.owner.id if i.owner else 0,
                                            'name':i.owner.fullname if i.owner else None
                                            },
                                   'description':i.description,
                                   'content_type':i.content_type,
                                   'datetime':i.modified_on}
                                for i in assets]

            data['id'] = target.id
            data['container'] = target.container
            data['holdAssets'] = target.holdAssets
            data['uuid'] = target.uuid
            data['path'] = target.path
            data['description'] = target.description
            data['repository'] = {'name':target.repository.name, 'id':target.repository.id}
            if target.repository and target.repository.project:
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

            #if not os.path.isdir(newC.url):
            req.session.add(newC)
            resp.body = {'message':'OK', 'info':'Collection created'}
            #else:
            #    resp.body = {'message':'ERROR', 'info':'Collection is available on server'}


class AssetCheckout:
    def on_post(self, req, resp, assetId):
        '''Get asset thumbnails from riak'''
        try:
            target = req.session.query(Asset).filter_by(id=int(assetId)).first()
        except ValueError:
            resp.status = falcon.HTTP_404
            return
        from tasks import process
        from utils.defaults import ASSETS
        asset_folder = os.path.join(ASSETS, target.uuid)
        if not os.path.isdir(asset_folder):
            resp.status = falcon.HTTP_404
            return

        version = req.get_param('version')
        command = 'checkout %s' % version
        arg = 'git --git-dir="{d}/.git" --work-tree="{d}" {c}'.format(d=asset_folder, c=command)
        error, result = process(arg)
        pstKey = '%s_poster_v%s'%(target.uuid, version.split('_')[1])
        thmbKey = '%s_thmb_v%s'%(target.uuid, version.split('_')[1])
        poster =  os.path.join('uploads', target.uuid + '_poster_' + version.split('_')[1] + '.png')
        thumbnail =  os.path.join('uploads', target.uuid + '_thmb_' + version.split('_')[1] + '.png')
        fid = target.uuid + '_preview_' + version.split('_')[1]
        fmt = 'ogv'
        preview =  os.path.join('uploads', fid+'.'+fmt)
        resp.body = {'poster':poster, 'thumbnail':thumbnail, 'version':version, 'preview':preview}


        

 
        
        


        
