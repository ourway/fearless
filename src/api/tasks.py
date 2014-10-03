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



import requests
import logging
import utils
import sys
import os
import ujson
import hashlib
import base64
from envelopes import Envelope, GMailSMTP
from utils.validators import email_validator
from opensource.contenttype import contenttype
from model import file_bucket, TeamClient  ## riak bucket for our files
from riak import RiakObject
import shutil
from utils.fagit import GIT
from datetime import datetime

BROKER_URL = 'amqp://guest:guest@localhost:5672//'
#BACKEND_URL = 'amqp'
BACKEND_URL = 'redis://localhost:6379/0'


#BROKER_URL = 'redis://localhost:6379/0'
#BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery
from utils.validators import checkPath

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
    if length: ## there is something
        length = int(length)/1024.0
        data = {'message':'OK', 'length':length, 
                'basename':basename}
    else:
        data = {'message':'ERROR'}
    return ujson.dumps(data)


@app.task
def add_asset(user, reponame, filepath):
    '''Add asset to database'''
    if not (b64 or path):
        return 'Not b64 or path'

    name = None
    content_type = contenttype('.%s' % ext)
    if b64:
        name = hashlib.md5(user+reponame+b64).hexdigest() + '.' + ext
    #################### riak part ################################
    if path and os.path.isfile(path):
        exts = path.split('.')
        if len(exts)>1:
            ext= exts[-1]
        name = hashlib.md5(user+reponame+path).hexdigest() + '.' + ext
        content_type = contenttype(path)
#        if os.path.getsize(path)<5*1024:
#            with open(path, 'rb') as f:
#                b64 = base64.encodestring(f.read())
#                name = hashlib.md5(b64).hexdigest() + '.' + ext


    if name and not file_bucket.get(name).exists:
        obj = RiakObject(TeamClient, file_bucket, name)
        obj.content_type = 'application/json'
        data = {'path':path, 
                'content_type':content_type,
                'ext':ext,
                'user':user,
                'repo':reponame,
                'datetime':datetime.utcnow()}
        obj.data = ujson.dumps(data)
        obj.store()
        print '\Info for {name} added to riak db\n'.format(name=name)

    elif name and file_bucket.get(name).exists:
        print 'File {name} is already available'.format(name=name)

    
    if name:
        file_path = os.path.join(STORAGE, user, reponame, name)

        if not os.path.isfile(file_path):
            if not os.path.isdir(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            if b64:
                with open(file_path, 'wb') as f:
                    f.write(base64.decodestring(b64))
            elif path and os.path.isfile(path):
                shutil.copyfile(path, file_path)

            print '\nFile {name} added to cache\n'.format(name=file_path)
        else:
            print '\nFile {name} was available\n'.format(name=file_path)

        repo = GIT(file_path)  ## do git operations
        repo.add()
        return name
        
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
    

