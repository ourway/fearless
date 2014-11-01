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
from sqlalchemy.ext import associationproxy


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
