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

import elasticsearch
import requests
import os
from envelopes import Envelope, GMailSMTP
from validators import email_validator
from opensource.contenttype import contenttype
# riak bucket for our files
from mako.template import Template
from fagit import GIT
from sqlalchemy.exc import IntegrityError  # for exception handeling
from mako.template import Template
templates_folder = os.path.join(os.path.dirname(__file__), 'templates')
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# BACKEND_URL = 'amqp'
# BACKEND_URL = 'redis://localhost:6379/0'

__all__ = ['app', 'download', 'add_asset', 'send_envelope']

BROKER_URL = 'redis://localhost:6379/0'
CELERYD_POOL = 'gevent'
BACKEND_URL = 'redis://localhost:6379/1'
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
    if length:  # there is something
        length = int(length) / 1024.0
        data = {'message': 'OK', 'length': length,
                'basename': basename}
    else:
        data = {'message': 'ERROR'}
    return ujson.dumps(data)


class mydatatype(object):
    pass


@app.task
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


@app.task
def remove_asset(name):
    pass


@app.task
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








@app.task()
def show_secrets(stream):
    return stream
