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
import model

db = model.getdb()

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
        


