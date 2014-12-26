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

import falcon
import os
from sqlalchemy.exc import IntegrityError  # for exception handeling
import ujson as json
import commands
import cStringIO
from sqlalchemy.ext import associationproxy
import datetime
import time
import csv
import base64
import uuid
from opensource.contenttype import contenttype


def process(cmd):
    '''General external process'''
    from gevent.subprocess import Popen, PIPE, call  # everything nedded to handle external commands
    p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE,
            )
            #universal_newlines=True)  # process
    (stdout, stderr) = p.communicate()
    return (stdout, stderr)


def get_ip():
    '''Simple method'''
    ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    return ip

def Commit():
    from models import session
    try:
        session.commit()
        return True
    except Exception, e:
        print '*'*80
        print e
        print '*'*80
        session.rollback()



def commit(req, resp):
        if not Commit():
            resp.status = falcon.HTTP_500
            resp.body = {'message':'Database Error'}





def jsonify(self, resp):
    '''Everything is json here'''
    if isinstance(resp.body, associationproxy._AssociationList):
        #resp.body = str(resp.body)
        resp.body = repr(resp.body)
    elif isinstance(resp.stream, (file, cStringIO.OutputType)):
        return
    elif isinstance(resp.body, (file, cStringIO.OutputType)):
        return
    else:
        try:
            json.loads(resp.body)
            data = resp.body
        except:
            try:
                data = json.dumps(resp.body)
            except:
                data = resp.body
        finally:

            resp.body = str(data)


def punish(self, req, resp):
    '''Add a user to database'''
    sid = req.cookie('session-id')
    if sid and r.get('fail_' + sid):
        resp.body = {
            'message': 'error', 'info': 'You need to wait!', 'wait': 5}
        return



def get_params(stream, flat=True):
    '''Return a string out of url params for query
    '''
    if not stream:
        return {}
    data = stream.read()
    if not data:
        return {}
    stream = json.loads(data)
    if not flat:
        return stream
    l = ','.join(['%s="%s"' % (i, stream[i]) for i in stream])
    return l


def parse_tjcsv(csvfile):
    csvfile.seek(0);
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    keys = spamreader.next()
    all = list(spamreader)
    obj = {}
    count = 0
    for s in all:
        idi = keys.index('Id')
        _id = s[idi]
        _id = _id.split('.')
        tid = None
        pid = None
        typ = 'root'
        if len(_id) == 2:
            pid = _id[1][2:]
            obj[count] = {'type':'project', 'projectid':pid}
        elif len(_id)>2:
            tid = _id[-1][1:]
            obj[count] = {'type':'task', 'taskid':tid}
        
        for key in keys:
            index = keys.index(key)
            value = s[index].strip()
            if key in ['Start', 'End']:
                value = s[index]
                format = '%y-%m-%d %H-%M'
                dt = datetime.datetime.strptime(value, format)
                value =  time.mktime(dt.timetuple())
            if tid or pid:
                obj[count][key.strip().lower()] = value
        count += 1
    
    return obj


def generateImageThumbnail(path, w=146, h=110, text=None):
    '''generate thumbnails using convert command'''
    content_type = contenttype(path)
    fmt = 'png'
    extra = ''
    page=''
    if content_type == 'image/vnd.adobe.photoshop':
        extra = '-flatten'
    if content_type == 'application/pdf':
        page = '[0]'
    newthmbPath = os.path.join('/tmp', str(uuid.uuid4())+'.png')
    cmd = 'convert "%s%s" -resize %sx%s %s "%s"' % (path,page, w, h, extra, newthmbPath)
    pr = process(cmd)
    if os.path.isfile(newthmbPath):
        with open(newthmbPath, 'rb') as newThumb:
            webmode = 'data:image/%s;base64,' % fmt
            return webmode + base64.encodestring(newThumb.read())


    

