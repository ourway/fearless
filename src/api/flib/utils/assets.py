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

import time
import hashlib
from cStringIO import StringIO
import falcon
import cPickle as pickle
from slugify import slugify, slugify_filename
from urllib import unquote
import os
import cgi
import uuid
from flib.utils.helpers import commit, Commit, get_params
from sys import stderr
from os import path
from flib.opensource.contenttype import contenttype
from flib.utils.validators import checkPath
from base64 import encode, decode, decodestring
from sqlalchemy import desc, asc
from datetime import datetime
import arrow

# from celery.result import AsyncResult
from flib.models import Asset, Repository, Collection, User, Task, fdb
from flib.utils.AAA import getUserInfoFromSession
from flib.utils.defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS
from flib.models.mixin import getUUID
from flib.utils.general import setup_logger

logger = setup_logger('auth', 'assets.log')


def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]


'''
This is a funtion that lets api to get a big/small file from user.

'''

#@asset_api.post('/save/<user>/<repo>')


class AssetSave:

    def on_put(self, req, resp, repo):
        ''' Get data based on a file object or b64 data, save and commit it
            repo can be repository name or id.

        '''
        cr = req.headers.get('CONTENT-RANGE')
        userInfo = getUserInfoFromSession(req, resp)
        uploader = userInfo.get('id')

        try:
            repo = int(repo)
            targetRepo = Repository.query.filter_by(id=repo).first()
        except ValueError:
            targetRepo = Repository.query.filter_by(name=repo).first()

        if not uploader:
            uploader = -1
            targetRepo = Repository.query.filter_by(name='public').first()

        targetUser = User.query.filter_by(id=uploader).first()

        if not targetRepo:
            targetRepo = Repository.query.filter_by(name=repo).first()
            if not targetRepo:
                targetRepo = Repository(
                    name=repo, path=os.path.join(public_repository_path, repo))
                req.session.add(targetRepo)

        ''' When client sends md5, it means that there is probabaly an exsisting file with that md5
            So we server doesnt need file data.  Just need to link old data '''
        _md5 = req.get_param('md5')
        tags = []
        _tags = req.get_param('tags')
        if _tags:
            tags = [tag.strip() for tag in _tags.split(',')]



        _cid = req.get_param('collection_id')
        collection = None
        if _cid:
            collection = Collection.query.filter_by(repository=targetRepo)\
                            .filter_by(id=_cid).first()
        _cname = req.get_param('collection')
        if _cname:
            collection = Collection.query.filter_by(repository=targetRepo)\
                            .filter_by(name=_cname).first()
        if not collection:
            now = arrow.utcnow()
            today = now.format('YYYY-MM-DD')
            cpath = '%s.%s'%(userInfo.get('alias'), today)
            collection = Collection.query.filter_by(path=cpath)\
                .filter_by(repository=targetRepo).first()
            if not collection:
                collection = Collection(path=cpath, repository=targetRepo)
                req.session.add(collection)



        _subpath = req.get_param('subpath')
        if _subpath:
            sub_collections = _subpath.strip().split('/')[:-1]
            _scp = None
            for sc in sub_collections:
                scdb = Collection.query.filter_by(repository=targetRepo)\
                    .filter_by(parent=_scp or collection).filter_by(name=sc).first()
                if not scdb:
                    scdb = Collection(path=sc, parent=_scp or collection, repository=targetRepo)
                    req.session.add(scdb)
                    req.session.flush()
                _scp = scdb

            if sub_collections:
                collection = scdb  ## set collection to last subpath folder


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
                resp.body = {'message': 'Error in myltipart data'}
                return
            _cgi_data = fs['files[]']
            body = _cgi_data.file

            if fs.has_key('thumbnail'):  # thumbnails are dataURLs
                thumbnail = fs['thumbnail'].file.read()

            mtname = _cgi_data.filename
        attach_to = req.get_param('attach_to')
        if targetRepo and (body or _md5):
            if not mtname:
                name = req.get_param(
                    'name') or 'undefined.%s.raw' % _generate_id()
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
            #name = os.path.basename(tempraryStoragePath)
            if _md5:
                availableAsset = Asset.query.filter_by(key=_md5).join(
                    Collection).filter_by(repository_id=targetRepo.id).first()
                if availableAsset:
                    # create folder if not available
                    checkPath(os.path.dirname(tempraryStoragePath))
                    if os.path.isfile(tempraryStoragePath):
                        os.remove(tempraryStoragePath)
                    os.symlink(availableAsset.full_path, tempraryStoragePath)
                    bodyMd5 = _md5
                else:
                    resp.status = falcon.HTTP_404
                    return
            else:
                if body:
                    bodyMd5 = safeCopyAndMd5(
                        req, body, tempraryStoragePath, targetRepo.id, targetUser, b64=b64, content_range=cr)

                    # in uploading progress
                    if bodyMd5 in ['IN_PROGRESS', 'IN_PROGRESS_NEW']:
                        resp.body = {'info': bodyMd5}
                        resp.status = falcon.HTTP_206
                        return
                else:
                    resp.status = falcon.HTTP_204
                    return

            fullname = name
            name = (name[:10] + '..') if len(name) > 10 else name
            asset = Asset.query.filter(
                Asset.repository == targetRepo).filter_by(collection=collection)\
                .filter_by(fullname=fullname).first()
            resp.status = falcon.HTTP_200
            if not asset:
                _uid = getUUID()
                asset = Asset(key=bodyMd5, version=1, repository=targetRepo, uuid=_uid,
                              collection=collection, name=name, fullname=fullname,
                              path=assetPath, ext=assetExt, owner_id=targetUser.id)
                req.session.add(asset)
                resp.status = falcon.HTTP_201
            else:
                if not bodyMd5 == asset.key:
                    asset.version += 1
                asset.name = name
                asset.fullname = fullname
                asset.key = bodyMd5
            # Asset descriptionspath
            asset.path = assetPath
            if req.get_param('description'):
                asset.description = req.get_param('description')
            if targetUser:
                asset.modifiers.append(targetUser)
                asset.users.append(targetUser)
            if thumbnail:  # thumbnail is base64 format
                fmt = 'png'
                fid = asset.uuid + '_thmb_' + str(asset.version)
                result = os.path.join('uploads', fid + '.' + fmt)
                thmbpath = os.path.join(public_upload_folder, fid + '.' + fmt)
                thmb_data = decodestring(unquote(thumbnail).split(',')[1])
                with open(thmbpath, 'wb') as f:
                    f.write(thmb_data)
            if attach_to:
                parent_id = int(attach_to)
                parent = Asset.query.filter_by(id=parent_id).first()
                asset.attached_to.append(parent)

            task_id = req.get_param('task_id')
            if task_id:
                target_task = Task.query.filter_by(id=task_id).first()
                target_task.assets.append(asset)

            if tags:
                asset.tags += tags
                collection.tags += tags
            req.session.flush()
            resp.body = {'key': asset.key, 'id':asset.id,
                         'url': asset.url, 'fullname': asset.fullname, 'uuid': asset.uuid,
                         'name': asset.name, 'content_type': asset.content_type.split('/')[0],
                         'datetime': time.time()}
            #resp.body = "I am working"
        else:  # lets consume the stream!
            while True:
                chunk = req.stream.read(2 ** 22)
                if not chunk:
                    break

            resp.status = falcon.HTTP_400
            resp.body = {'message': 'Something Wrong!'}


def safeCopyAndMd5(req, fileobj, destinationPath, repoId, uploader, b64=False, content_range=False):
    '''copy a file in chunked mode safely'''

    destDir = path.dirname(destinationPath)
    extsp = destinationPath.split('.')
    if len(extsp) > 1:
        ext = extsp[1]
    else:
        ext = 'raw'
    checkPath(destDir)

    ''' if available asset, then we need to symblink it if asset uuid if different than available one!'''

    start_byte = 0
    in_progress = False
    if content_range:
        in_progress = True
        _bp = content_range.split()
        # a simple validation:
        if len(_bp) == 2 and len(_bp[1].split('/')) == 2:
            _bd = _bp[1].split('/')
            start_byte, eb = map(int, _bd[0].split('-'))
            tb = int(_bd[-1])
            if tb == eb + 1:
                in_progress = False

    if os.path.islink(destinationPath):
        os.remove(destinationPath)

    if not start_byte:  # if its a new file
        if os.path.isfile(destinationPath):
            os.remove(destinationPath)

    with open(destinationPath, 'a+') as f:
        md5 = hashlib.md5()
        if b64:
            b = StringIO()
            decode(fileobj, b)
            b.seek(0)
            fileobj = b
        while True:
            chunk = fileobj.read(2 ** 24)  # 4 megs
            # chunk = fileobj.read(1024) ## 1Kb
            if not chunk:
                break
            md5.update(chunk)
            f.write(chunk)
    if in_progress and not start_byte:
        return 'IN_PROGRESS_NEW'

    if in_progress:
        return 'IN_PROGRESS'

    dataMd5 = md5.hexdigest()
    # check if there is an asset with same key
    if not repoId:
        availableAsset = Asset.query.filter_by(key=dataMd5).first()
    else:
        availableAsset = req.session.query(Asset).filter_by(key=dataMd5).join(
            Collection).filter_by(repository_id=repoId).first()

    '''First lets clean asset is there no files linked to it'''
    if availableAsset:
        if not os.path.isfile(availableAsset.full_path):
            req.session.delete(availableAsset)

        elif not availableAsset.full_path == destinationPath:
            os.remove(destinationPath)  # we dont need it anymore
            os.symlink(availableAsset.full_path, destinationPath)
            # print 'Symblink: %s generated' % destinationPath

    return dataMd5

'''
def getAssetInfo(key):
    'Get asset Info based on key or md5'

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

'''


class GetAsset:

    def on_post(self, req, resp, key):
        '''Serve asset based on a key (riak key for finding path'''
        name = req.get_param('name')
        if name == 'true':
            target = Asset.query.filter_by(fullname=key).first()
        else:
            target = Asset.query.filter_by(key=key).first()
        if target:
            sz = os.path.getsize(target.full_path)
            modifier = target.modifiers[-1]
            attachments = [
                {
                    'name': i.name,
                    'url': i.url,
                    'id': i.id,
                    'description': i.description,
                    'thumbnail': i.thumbnail,
                    'content_type': i.content_type
                }
                for i in target.attachments]
            resp.body = {'url': os.path.join('/static', target.url),
                         'size': sz, 'key': target.key, 'id': target.id,
                         'version': target.version, 'datetime': target.modified_on,
                         'last_updated_by': modifier.alias, 'descripion': target.description,
                         'owner': target.owner.alias, 'thumbnail': target.thumbnail,
                         'attachments': attachments}


class DeleteAsset:

    def on_delete(self, req, resp, id):
        target = Asset.query.filter_by(id=id).first()
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



class ZipCollection:
    def on_get(self, req, resp, collectionId):
        target_collection = Collection.query.filter_by(id=int(collectionId)).scalar()
	if target_collection:
        	target_repository = Repository.query\
			.filter_by(id=target_collection.repository_id).scalar()
		
		collection_folder = os.path.join(target_repository.path, target_collection.path)

		#home_folder = os.path.join(os.getenv('HOME'), '.fearlessrepo')
		home_folder = '/home/fearless/.fearlessrepo'
		tar_folder = os.path.join(home_folder, 'uploads')
		tarfile = os.path.join(tar_folder, target_collection.uuid + '.tar').replace('-', '').replace('+', '')
		cmd = 'tar -cvf "{o}" "{s}"'.format(o=tarfile, s=collection_folder) 
		os.system(cmd)
		resp.status = falcon.HTTP_201
		resp.body = dict(result=os.path.relpath(tarfile, home_folder))
 


class CollectionInfo:

    def on_get(self, req, resp, collectionId):
        target = Collection.query.filter_by(id=int(collectionId)).first()
        start = req.get_param('s')
        end = req.get_param('e')
        if start:
            start = int(start)
        else:
            start = 0
        if end:
            end = int(end)
        if start != None and not end:
            end = start + 50

        end = max(start, end)

        if target:
            assets = Asset.query.filter_by(collection_id=target.id).order_by(
                desc(Asset.modified_on)).order_by(desc(Asset.name)).slice(start, end)
            assets_count = Asset.query.filter_by(collection_id=target.id).count()
            data = dict()
            data['name'] = target.name
            data['name'] = target.name
            data['assets_count'] = assets_count
            if assets:
                data['assets'] = [
                    {'id': i.id,
                     'name': i.name,
                     'uuid': i.uuid,
                     'url': i.url,
                     'content_size': i.content_size,
                     'fullname': i.fullname,
                     'version': i.version,
                     'thumbnail': i.thumbnail,
                     'preview': i.preview,
                     'poster': i.poster,
                     'owner': {
                         'id': i.owner.id if i.owner else 0,
                         'name': i.owner.fullname if i.owner else None
                     },
                     'description': i.description,
                     'content_type': i.content_type,
                     'datetime': i.modified_on}
                    for i in assets]

            data['id'] = target.id
            data['container'] = target.container
            data['holdAssets'] = target.holdAssets
            data['collection_size'] = target.collection_size
            data['uuid'] = target.uuid
            data['owner_id'] = target.owner_id
            data['created_on'] = target.created_on
            data['modified_on'] = target.modified_on
            data['path'] = target.path
            data['description'] = target.description
            data['repository'] = {
                'name': target.repository.name, 'id': target.repository.id}
            if target.repository and target.repository.project:
                data['project'] = {
                    'name': target.repository.project.name, 'id': target.repository.project.id}
            _t = target.parent
            d = data
            while True:
                if _t:
                    d['parent'] = {
                        'name': _t.name, 'id': _t.id, 'path': _t.path}
                    d = d['parent']
                    _t = _t.parent
                else:
                    break
            if target.children:
                data['children'] = [{'name': i.name, 'id': i.id,
                                     'collection_size':i.collection_size, 'path': i.path, 'number_of_assets': i.number_of_assets,
                                     'children': [{'name': c1.name, 'id': c1.id, 'path': c1.path, } for c1 in i.children]
                                     } for i in target.children]
            resp.body = data


class AddCollection:

    def on_put(self, req, resp):
        userInfo = getUserInfoFromSession(req, resp)
        data = get_params(req.stream, flat=False)
        name = data.get('name')
        repository_id = data.get('repository_id')
        parent_id = data.get('parent_id')

        template = data.get('template').lower()
        if name and repository_id:
            _uid = getUUID()
            newC = Collection( name=name, uuid=_uid, path=name,
                              repository_id=repository_id, owner_id=userInfo.get('id'))
            if parent_id:
                newC.parent_id = parent_id
            if template:
                newC.template = template

            # if not os.path.isdir(newC.url):
            req.session.add(newC)
            req.session.flush()
            resp.body = {'message': 'OK', 'info': {'uuid': _uid}}
            # else:
            #    resp.body = {'message':'ERROR', 'info':'Collection is available on server'}


class AssetCheckout:

    def on_post(self, req, resp, assetId):
        '''Get asset thumbnails from riak'''
        try:
            target = Asset.query.filter_by(id=int(assetId)).first()
        except ValueError:
            resp.status = falcon.HTTP_404
            return
        userInfo = getUserInfoFromSession(req, resp)
        from flib.tasks import process
        from flib.utils.defaults import ASSETS
        asset_folder = os.path.join(ASSETS, target.uuid)
        if not os.path.isdir(asset_folder):
            resp.status = falcon.HTTP_204  # empty content
            return

        version = req.get_param('version')
	print version
	if not (version and len(version.split('_'))>1):
		resp.status = falcon.HTTP_404
		return
        command1= 'pull origin master'
        command2= 'pull origin master --tags'
        command3= 'checkout %s' % version
        arg1 = 'git --git-dir="{d}/.git" --work-tree="{d}" {c}'.format(
            d=asset_folder, c=command1)
        arg2 = 'git --git-dir="{d}/.git" --work-tree="{d}" {c}'.format(
            d=asset_folder, c=command2)
        arg3 = 'git --git-dir="{d}/.git" --work-tree="{d}" {c}'.format(
            d=asset_folder, c=command3)

        LOCK = os.path.join(asset_folder, 'LOCK')
        if os.path.isfile(LOCK):
            LD = pickle.load(open(LOCK, 'rb'))
            now = datetime.utcnow()
            locktime = LD.get('datetime')
            if locktime and (now-locktime).seconds < 15:  ## 15 seconds is maximum time for checking out
                resp.status = falcon.HTTP_202
                resp.body = {'message':'File is busy. try again'}
                return

        LD = {'datetime':datetime.utcnow(), 'user':userInfo.get('lastname')}
        pickle.dump(LD, open(LOCK, 'wb'))
        error1, result1 = process(arg1)  ## pull
        error2, result2 = process(arg2)  ## tags
        error3, result3 = process(arg3)  ## checkout
        pstKey = '%s_poster_v%s' % (target.uuid, version.split('_')[1])
        thmbKey = '%s_thmb_v%s' % (target.uuid, version.split('_')[1])
        poster = os.path.join(
            'uploads', target.uuid + '_poster_' + version.split('_')[1] + '.png')
        thumbnail = os.path.join(
            'uploads', target.uuid + '_thmb_' + version.split('_')[1] + '.png')
        fid = target.uuid + '_preview_' + version.split('_')[1]
        fmt = 'mp4'
        preview = os.path.join('uploads', fid + '.' + fmt)
        if os.path.isfile(LOCK):
            os.remove(LOCK)
        resp.body = {'poster': poster, 'thumbnail': thumbnail,
                     'version': version, 'preview': preview}


class TestUpload:

    def on_put(self, req, resp):
        print 'uploading'
        obj = req.stream
        print 'got stream'

        with open('/home/fearless/Desktop/upload', 'a+') as f:
            while True:
                chunk = obj.read(1024)
                if not chunk:
                    break
                f.write(chunk)
                print 'chunk'

        resp.status = falcon.HTTP_201
