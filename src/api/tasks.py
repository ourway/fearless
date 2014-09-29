#!/usr/bin/env python
# -*- coding: utf-8 -*-

_copyright = 'Chista Co.'
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

from model import file_bucket, TeamClient  ## riak bucket for our files
from riak import RiakObject


BROKER_URL = 'amqp://guest:guest@localhost:5672//'
#BACKEND_URL = 'amqp'
BACKEND_URL = 'redis://localhost:6379/0'


#BROKER_URL = 'redis://localhost:6379/0'
#BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery

app = Celery('tasks',
                broker=BROKER_URL,
                backend=BACKEND_URL,
                include=[])

storage = '../views/cache'
if not os.path.isdir(storage):
    os.makedirs(storage)
STORAGE = os.path.abspath(storage)

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
def add_asset(b64=None, path=None):
    name = None
    if b64:
        name = hashlib.md5(b64).hexdigest()
    elif path:
        with open(path, 'rb') as f:
            b64 = base64.encodestring(f.read())
            name = hashlib.md5(b64).hexdigest()

    if b64 and not file_bucket.get(name).exists:
         
        obj = RiakObject(TeamClient, file_bucket, name)
        obj.content_type = 'application/json'
        data = {'base64':b64, 'path':path}
        obj.data = ujson.dumps(data)
        obj.store()
        print '\nFile {name} added to riak db\n'.format(name=name)

    elif file_bucket.get(name).exists:
        print 'File {name} is already available'.format(name=name)

    file_path = os.path.join(STORAGE, name)
    if not os.path.isfile(file_path):
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
                f.write(base64.decodestring(b64))
        print '\nFile {name} added to cache\n'.format(name=file_path)
    else:
        print '\nFile {name} was available\n'.format(name=file_path)

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
    

