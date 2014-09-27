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
import uwsgi
import hashlib
from validators import email_validator
from model import getdb
from tasks import send_envelope


db=getdb()

def clean(req, resp, *kw):
    #print kw
    #print dir(db)
    db.commit()
    #db.close()


class Mailer(object):
    def on_post(self, req, resp, **kw):
        '''send an email'''
        data = {'message':'Error'}
        to = req.get_param('to')
        subject = req.get_param('subject')
        message = req.get_param('message')
        attach = req.get_param('attach')
        if subject and to and message:
            mail = send_envelope.delay(to, subject, message, attach)
            data = {'message':'ok', 'task_id':mail.task_id}
        else:
            resp.status = falcon.HTTP_400
        resp.body=ujson.dumps(data)
