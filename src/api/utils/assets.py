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


import bottle
import ujson
import sys, time
from os import path
from model import getdb
from tasks import add_asset
from tasks import remove_asset
from tasks import STORAGE
from utils.fagit import GIT
from utils.validators import checkPath
#from celery.result import AsyncResult

import base64
import hashlib
from opensource.contenttype import contenttype
from model import file_bucket  ## riak bucket for our files
from riak import RiakObject  ## riak bucket for our files


asset_api = bottle.Bottle()

def _generate_id():
    return os.urandom(2).encode('hex') + hex(int(time.time() * 10))[5:]

'''
This is a funtion that lets api to get a big/small file from user.

'''


@asset_api.post('/asset/<user>/<repo>/<assetName>')
def addNewAsset(user, repo, assetName):
    targetNewFilePath = path.abspath(path.join(STORAGE, user, repo, assetName))
    checkPath(path.dirname(targetNewFilePath))
    uploadByFileMethod = bottle.request.files.get('asset')
    if uploadByFileMethod:
        uploadByFileMethod.save(targetNewFilePath, overwrite=True) # appends upload.filename automatically
    return 'OK'
