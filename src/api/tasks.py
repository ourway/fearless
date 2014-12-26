#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an apology!
Clean code is much better than Cleaner comments!
'''

'''
@desc: tasks.py
@c: Chista Co
@author: F.Ashouri
@version: 0.1.8
'''

from gevent import monkey; monkey.patch_all()
import ujson
import hashlib
import base64
import shutil
from datetime import datetime

import elasticsearch
import requests
import os
import uuid
from envelopes import Envelope, GMailSMTP
from utils.validators import email_validator
from models import session
from opensource.contenttype import contenttype
# riak bucket for our files
import sh
from mako.template import Template
from utils.fagit import GIT
from sqlalchemy.exc import IntegrityError  # for exception handeling
from mako.template import Template
from utils.defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS

current_dir = os.path.abspath(os.path.dirname(__file__))
ffmpeg = os.path.join(current_dir, '../../bin/ffmpeg/ffmpeg')
ffprobe = os.path.join(current_dir, '../../bin/ffmpeg/ffprobe')


templates_folder = os.path.join(os.path.dirname(__file__), 'templates')
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# BACKEND_URL = 'amqp'
# BACKEND_URL = 'redis://localhost:6379/0'


BROKER_URL = 'redis://localhost:6379/0'
BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery

from utils.validators import checkPath, md5_for_file


Capp = Celery('tasks',
             broker=BROKER_URL,
             backend=BACKEND_URL,
             include=[])

storage = '../../STATIC'
STORAGE = checkPath(storage)


def process(cmd):
    '''General external process'''
    from gevent.subprocess import Popen, PIPE, call  # everything nedded to handle external commands
    p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE,
            )
            #universal_newlines=True)  # process
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)










@Capp.task
def download(url):
    basename = url.split('/')[-1]
    r = requests.head(url)
    length = r.headers.get('content-length')
    if length:  # there is something
        length = int(length) / 1024.0
        data = {'message': 'OK', 'length': length,
                'basename': basename}
    else:
        data = {'message': 'ERROR'}
    return ujson.dumps(data)


class mydatatype(object):
    pass


@Capp.task
def add_asset(dataMD5, uploadedFilePath):
    ''' Add asset to database
        Why I provide the md5? Cause we can get md5 in uploading process before.
    '''
    if not uploadedFilePath:
        return 'Not any path'

    targetAsset = session.query(Asset).filter(Asset.key == dataMD5).first()
    if not targetAsset:
        print 'Target asset is not available!'
        return
    task_id = add_asset.request.id
    originalName = os.path.basename(uploadedFilePath)
    targetAsset.ext = originalName.split('.')[-1]
    targetAsset.content_type = contenttype(uploadedFilePath)
    targetAsset.path = os.path.join(os.path.relpath(os.path.dirname(uploadedFilePath),
                                                    targetAsset.repository.path) or '', dataMD5 + '.' + targetAsset.ext)
    print '*' * 80
    print targetAsset.path
    print '*' * 80
    obj = mydatatype()
    obj.content_type = 'application/json'
    data = {'path': uploadedFilePath,
            'content_type': targetAsset.content_type,
            'ext': targetAsset.ext,
            'originalName': targetAsset.name,
            'md5': targetAsset.key,
            'key': task_id,
            'asset': targetAsset.id,
            'repository': targetAsset.repository.id,
            'datetime': datetime.utcnow()}
    obj.data = ujson.dumps(data)
    try:
        es.create(
            index='assets2', doc_type='info', body=obj.data)
    except elasticsearch.ConflictError:
        pass

    # repo = GIT(uploadedFilePath)  ## do git operations
        # repo.add('{user}->{repo}->{originalName}' \
        #         .format(user=userName,
        #                 repo=repositoryName,
        #                 originalName=originalName))

    try:
        session.commit()
        return targetAsset.key
    except IntegrityError:
        return 'Error'


@Capp.task
def remove_asset(name):
    pass


@Capp.task
def send_envelope(to, cc, bcc, subject, message, attach=None):

    _et = os.path.join(templates_folder, 'email.html')
    ET = Template(filename=_et)
    M = ET.render(message=message, subject=subject)
    envelope = Envelope(
        from_addr=(u'farsheed.ashouri@gmail.com',
                   u'Pooyamehr Fearless Notification'),
        to_addr=to,
        cc_addr=cc,
        bcc_addr=bcc,
        subject=subject,
        html_body=M
    )
    #envelope.add_attachment('/home/farsheed/Desktop/guntt.html', mimetype="text/html")

    if attach and os.path.isfile(attach):
        envelope.add_attachment(attach)

    pwd = '\n==gchZmcoVWbwADMxM2Q'[::-1]

    gmail = GMailSMTP('farsheed.ashouri@gmail.com',
                      base64.decodestring(pwd))
    gmail.send(envelope)








@Capp.task()
def show_secrets(stream):
    return stream




###########################################################################
def duration(path):
    '''Find video duration'''
    path = path.encode("utf-8")
    arg = '''nice "%s" -show_format "%s" 2>&1''' % (ffprobe, path)
    pr = process(arg)
    dupart = pr[0].split('duration=')  # text processing output of a file
    if pr and len(dupart) > 1:
        du = dupart[1].split()[0]
        try:
            return float(du)
        except ValueError:
            return

@Capp.task
def addFileToGit(path, assetUuid, version):
    path = path.encode("utf-8")
    directory = os.path.dirname(path)
    git_dir = os.path.join(GIT_folder, assetUuid)
    filename = os.path.basename(path)
    ## initilize
    command = 'init'
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(d=directory, g=git_dir, c=command)
    process(arg)
    ## add file
    command = 'add "%s"' % filename
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(d=directory, g=git_dir, c=command)
    process(arg)
    ## add tag based on new version and uuid
    ## commit
    command = 'commit -m "file: %s added."' % filename
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(d=directory, g=git_dir, c=command)
    commit, error = process(arg)
    command = 'tag v_%s' % version
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(d=directory, g=git_dir, c=command)
    process(arg)
    ## now lets clone it to assets folder
    asset_folder = os.path.join(ASSETS, assetUuid)
    if not os.path.isdir(asset_folder):  ## not cloned
        command = 'git clone "%s" "%s"' % (git_dir, asset_folder)
        process(command)
    else:
        command = 'pull'
        arg = 'git --work-tree="{d}" --git-dir="{d}/.git" {c}'.format(d=asset_folder, c=command)
        process(arg)
 

def getTags(path, assetUuid):
    path = path.encode("utf-8")
    directory = os.path.dirname(path)
    git_dir = os.path.join(GIT_folder, assetUuid)
    command = 'tag -l'
    arg = 'git --work-tree="{d}" --git-dir="{g}" {c}'.format(d=directory, g=git_dir, c=command)
    result, error = process(arg)
    return ','.join(result.strip().split('\n'))


@Capp.task
def identify(path, assetId):
    '''Find video duration'''
    path = path.encode('utf-8')
    content_type = contenttype(path)
    if content_type.split('/')[0]=='image':
        arg = '''nice identify "%s" 2>&1''' % (path)
    else:
        arg = '''nice file "%s" 2>&1''' % (path)
    result, error = process(arg)
    if assetId:
        from models import Asset
        target = session.query(Asset).filter_by(id=assetId).first()
        if target and result:
            target.fileinfo = result.replace(path, '').strip()
            session.commit()


@Capp.task
def generateVideoThumbnail(path, w=146, h=110, text=None):
    '''generate a thumbnail from a video file and return a vfile db'''
    path = path.encode('utf-8')
    upf = '/tmp'
    #upf = '/home/farsheed/Desktop'
    fid = str(uuid.uuid4())
    fmt = 'png'
    thpath = '%s/%s.%s' % (upf, fid, fmt)
    arg = '''"%s" -i "%s" -an -r 1 -vf "select=gte(n\,100)" -vframes 1 -s %sx%s -y "%s"''' \
        % (ffmpeg, path, w, h, thpath)
    
    pr = process(arg)
    if os.path.isfile(thpath):
        with open(thpath, 'rb') as newThumb:
            webmode = 'data:image/%s;base64,' % fmt
            result =  webmode + base64.encodestring(newThumb.read())
        return result


@Capp.task
def generateVideoPreview(path, asset=None):
    path = path.encode('utf-8')
    '''generate a thumbnail from a video file and return a vfile db'''
    if asset:
        from models import Asset
        target = session.query(Asset).filter_by(id=asset).first()
    fid = str(uuid.uuid4())
    fmt = 'm4v'
    previewPath = os.path.join(public_upload_folder, fid+'.'+fmt)
    arg = '''"%s" -i "%s" -preset ultrafast -s hd480 "%s"''' \
        % (ffmpeg, path, previewPath)
    
    pr = process(arg)
    if os.path.isfile(previewPath):
        result =  os.path.join('uploads', fid+'.'+fmt)
        if asset and target:
            target.preview = result
            session.commit()
            return result

@Capp.task
def generateImageThumbnail(path, w=146, h=110, asset=None, text=None):
    '''generate thumbnails using convert command'''
    path = path.encode('utf-8')
    content_type = contenttype(path)
    fmt = 'png'
    extra = ''
    page=''
    if content_type == 'image/vnd.adobe.photoshop':
        extra = '-flatten'
    if content_type == 'application/pdf':
        page = '[0]'
    newthmbPath = os.path.join('/tmp', str(uuid.uuid4())+'.png')
    cmd = 'convert "%s%s" %s -resize %sx%s "%s"' % (path, page, extra, w, h, newthmbPath)
    pr = process(cmd)
    if os.path.isfile(newthmbPath):
        with open(newthmbPath, 'rb') as newThumb:
            webmode = 'data:image/%s;base64,' % fmt
            result = webmode + base64.encodestring(newThumb.read())

        if asset and result:
            from models import Asset
            target = session.query(Asset).filter_by(id=asset).first()
            target.pst = result;
            session.commit()

        

        return result

        #return os.path.realpath(public_repository_path, previewPath)

        
def getTimecode(frame, rate):
    '''Get standard timecode'''
    seconds = frame / rate
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    timecode = "%02d:%02d:%04f" % (h, m, s)
    return timecode


######################################################
######################################################
