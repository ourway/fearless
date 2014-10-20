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

from models import session

def commit(req, resp):
    try:
        session.commit()
    except IntegrityError, e:
        session.rollback()
        resp.status = falcon.HTTP_400
        resp.body = json.dumps(e)



def punish(self, req, resp):
    '''Add a user to database'''
    sid = req.cookie('session-id')
    if sid and r.get('fail_'+sid):
        resp.body = json.dumps({'message': 'error', 'info':'You need to wait!', 'wait':5})
        return
