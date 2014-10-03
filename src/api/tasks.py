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

import ujson
import hashlib
import base64
import shutil
from datetime import datetime

import requests
import os
from envelopes import Envelope, GMailSMTP
from utils.validators import email_validator
from opensource.contenttype import contenttype
from model import file_bucket, TeamClient  # # riak bucket for our files
from riak import RiakObject
from utils.fagit import GIT


BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# BACKEND_URL = 'amqp'
BACKEND_URL = 'redis://localhost:6379/0'


# BROKER_URL = 'redis://localhost:6379/0'
#BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery
from utils.validators import checkPath, md5_for_file

app = Celery('tasks',
             broker=BROKER_URL,
             backend=BACKEND_URL,
             include=[])

storage = '../../STATIC'
STORAGE = checkPath(storage)


@app.task
def download(url):
    basename = url.split('/')[-1]
    r = requests.head(url)
    length = r.headers.get('content-length')
    if length:  ## there is something
        length = int(length) / 1024.0
        data = {'message': 'OK', 'length': length,
                'basename': basename}
    else:
        data = {'message': 'ERROR'}
    return ujson.dumps(data)


@app.task
def add_asset(userName, repositoryName, b64Data=None,
              ext='json', uploadedFilePath=None):
    '''Add asset to database'''
    if not (b64Data or uploadedFilePath):
        return 'Not b64 or path'

    task_id = add_asset.request.id
    newFileName = None
    content_type = contenttype('.%s' % ext)
    if b64Data:
        dataMD5 = hashlib.md5(b64Data).hexdigest()
        newFileName = dataMD5 + '.' + ext
    #################### riak part ################################
    if uploadedFilePath and os.path.isfile(uploadedFilePath):
        exts = uploadedFilePath.split('.')
        if len(exts) > 1:
            ext = exts[-1]
        dataMD5 = md5_for_file(open(uploadedFilePath, 'rb'))
        newFileName = dataMD5 + '.' + ext
        content_type = contenttype(uploadedFilePath)
    #        if os.path.getsize(path)<5*1024:
    #            with open(path, 'rb') as f:
    #                b64 = base64.encodestring(f.read())
    #                newFileName = hashlib.md5(b64).hexdigest() + '.' + ext


    newFilePath = os.path.join(STORAGE, userName, repositoryName, newFileName)
    originalName = os.path.basename(uploadedFilePath) or 'Base64 Data'

    if newFileName and not file_bucket.get(newFileName).exists:
        obj = RiakObject(TeamClient, file_bucket, task_id)
        obj.content_type = 'application/json'
        data = {'path': newFilePath,
                'content_type': content_type,
                'ext': ext,
                'originalName': originalName,
                'md5': dataMD5,
                'user': userName,
                'repo': repositoryName,
                'datetime': datetime.utcnow()}
        obj.data = ujson.dumps(data)
        obj.store()
        print '\Info for {name} added to riak db\n'.format(name=newFileName)

    elif newFileName and file_bucket.get(newFileName).exists:
        print 'File {name} is already available'.format(name=newFileName)


    checkPath(os.path.abspath(os.path.dirname(newFilePath)))
    if b64Data:
        with open(newFileName, 'wb') as f:
            f.write(base64.decodestring(b64Data))
    elif uploadedFilePath and os.path.isfile(uploadedFilePath):
        shutil.copyfile(uploadedFilePath, newFilePath)

    print '\nFile {name} added to cache\n'.format(name=newFilePath)

    repo = GIT(newFilePath)  ## do git operations
    repo.add('{user}->{repo}->{originalName}' \
             .format(user=userName,
                     repo=repositoryName,
                     originalName=originalName))

    if newFilePath != uploadedFilePath:
        os.remove(uploadedFilePath)
    return newFileName


@app.task
def remove_asset(name):
    pass


@app.task
def send_envelope(to, subject, message, attach=None):
    envelope = Envelope(
        from_addr=(u'farsheed.ashouri@gmail.com',
                   u'Pooyamehr Animation System Notification'),
        to_addr=to,
        subject=subject,
        text_body=message
    )

    if attach and os.path.isfile(attach):
        envelope.add_attachment(attach)

    pwd = '\n==gchZmcoVWbwADMxM2Q'[::-1]
    gmail = GMailSMTP('farsheed.ashouri@gmail.com',
                      base64.decodestring(pwd))
    if email_validator(to):
        gmail.send(envelope)


@app.task()
def show_secrets(stream):
    return stream
