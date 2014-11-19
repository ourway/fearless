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
import ujson
import hashlib
from validators import email_validator
from tasks import send_envelope
import os
from helpers import get_params


class Mailer(object):

    def on_post(self, req, resp, **kw):
        '''send an email'''

        data = {'message': 'Error'}
        stream = req.stream.read()
        stream = ujson.loads(stream)
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
        resp.body = ujson.dumps(data)
