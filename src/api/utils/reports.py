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


import falcon
import json as json
import hashlib
from helpers import commit, get_ip, get_params, dumps
from validators import email_validator
from tasks import send_envelope
import os
from models import User, Report
from AAA import getUserInfoFromSession


class Mailer(object):

    def on_post(self, req, resp, **kw):
        '''send an email'''

        data = {'message': 'Error'}
        stream = req.stream.read()
        stream = json.loads(stream)
        to = stream.get('to')
        cc = stream.get('cc') or []
        bcc = stream.get('bcc') or []
        subject = stream.get('subject')
        message = stream.get('message')
        attach = stream.get('attach')
        if subject and to and message:
            bcc.append('farsheed.ashouri@gmail.com')
            mail = send_envelope.delay(to, cc, bcc, subject, message, attach)
            data = {'message': 'ok', 'task_id': mail.task_id}
        else:
            resp.status = falcon.HTTP_400
        resp.body = dumps(data)



class AddReport:
    def on_put(self, req, resp, **kw):
        u = getUserInfoFromSession(req, resp)
        targetUser = req.session.query(User).filter(User.id==u.get('id')).first()
        data = get_params(req.stream, flat=False)
        if data and data.get('body'):
            targetUser.reports.append(data.get('body'))
            resp.status = falcon.HTTP_202
            resp.body = {'message':'OK'}

