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
from models import session
from sqlalchemy.exc import IntegrityError  # for exception handeling
import ujson as json
import commands
import cStringIO


def get_ip():
    '''Simple method'''
    ip = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    return ip


def commit(req, resp):
    try:
        session.commit()
    except IntegrityError, e:
        session.rollback()
        resp.status = falcon.HTTP_400
        resp.body = e


def jsonify(self, resp):
    '''Everything is json here'''
    if isinstance(resp.stream, (file, cStringIO.OutputType)):
        return
    elif isinstance(resp.body, (file, cStringIO.OutputType)):
        return
    else:
        resp.body = json.dumps(resp.body)

    #resp.body = json.dumps(resp.body)


def punish(self, req, resp):
    '''Add a user to database'''
    sid = req.cookie('session-id')
    if sid and r.get('fail_' + sid):
        resp.body = {
            'message': 'error', 'info': 'You need to wait!', 'wait': 5}
        return
