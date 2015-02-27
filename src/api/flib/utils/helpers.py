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
from collections import defaultdict
import base64
import uuid
from flib.opensource.contenttype import contenttype


def get_ip():
    '''Simple method'''
    ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    return ip


def Commit():
    return True


def commit(req, resp):
    if not Commit():
        resp.status = falcon.HTTP_500
        resp.body = {'message': 'Database Error'}


def dumps(obj):
    return json.dumps(obj)


def jsonify(self, resp):
    '''Everything is json here'''
    if resp.stream:
        return
    resp.content_type = 'application/json'
    if not resp.body:
        data = '[]'
        resp.body = data
        return
    if isinstance(resp.body, (dict)):
        data = json.dumps(resp.body)
    elif isinstance(resp.body, (str)):
        data = json.dumps(resp.body)
    elif isinstance(resp.body, (list)):
        try:
            data = json.loads(repr(resp.body))
        except:
            data = resp.body
        finally:
            data = json.dumps(data)
    else:
        data = repr(resp.body)
    resp.body = data


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
    csvfile.seek(0)
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    try:
        keys = spamreader.next()
    except StopIteration:
        return
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
            obj[count] = {'type': 'project', 'projectid': pid}
        elif len(_id) > 2:
            tid = _id[-1][1:]
            obj[count] = {'type': 'task', 'taskid': tid}

        for key in keys:
            index = keys.index(key)
            value = s[index].strip()
            if key in ['Start', 'End']:
                value = s[index]
                format = '%y-%m-%d %H-%M'
                dt = datetime.datetime.strptime(value, format)
                value = time.mktime(dt.timetuple())
            if tid or pid:
                obj[count][key.strip().lower()] = value
        count += 1
    return obj


def csv2json(csvfile):
    '''A general function'''
    csvfile.seek(0)
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    try:
        keys = spamreader.next()
    except StopIteration:
        return
    all = list(spamreader)
    obj = defaultdict(list)
    count = 0
    for s in all:
        for key in keys:
            index = keys.index(key)
            value = s[index].strip()
            obj[key].append(value)
    return dict(obj)



