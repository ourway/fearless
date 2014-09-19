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
from model import file_bucket  ## riak bucket for our files


BROKER_URL = 'amqp://guest:guest@localhost:5672//'


#BROKER_URL = 'redis://localhost:6379/0'
#BACKEND_URL = 'redis://localhost:6379/1'
from celery import Celery

app = Celery('tasks',
                broker=BROKER_URL,
                backend='amqp',
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
def add_asset(name, b64):
    if not file_bucket.get(name).data:
        new = file_bucket.new(key=name, data={'base64':b64})
        new.store()
        print 'File {name} added to riak db'.format(name=name)
    else:
        print 'File {name} is already available'.format(name=name)
        
@app.task
def remove_asset(name):
    pass

