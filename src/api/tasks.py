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
from model import file_bucket, TeamClient  ## riak bucket for our files
from riak import RiakObject


BROKER_URL = 'amqp://guest:guest@localhost:5672//'
BACKEND_URL = 'amqp://guest:guest@localhost:5672//'


#BROKER_URL = 'redis://localhost:6379/0'
#BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery

app = Celery('tasks',
                broker=BROKER_URL,
                backend=BACKEND_URL,
                include=[])



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
    if b64:
        name = hashlib.md5(b64).hexdigest()
    elif path:
        with open(path, 'rb') as f:
            b64 = base64.encodestring(f.read())
            name = path
    if b64 and not file_bucket.get(name).exists: ##TODO fixme 
        obj = RiakObject(TeamClient, file_bucket, name)
        obj.content_type = 'application/json'
        data = {'base64':b64, 'path':path}
        obj.data = ujson.dumps(data)
        obj.store()
        print '\nFile {name} added to riak db\n'.format(name=name)
        return name
    elif file_bucket.get(name).exists:
        print 'File {name} is already available'.format(name=name)
        return name
        
@app.task
def remove_asset(name):
    pass

