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
from models import ddb, riakClient, User
from AAA import Authorize, getUserInfoFromSession
from helpers import get_params
import base64
from uuid import uuid4


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')



def getUserMessageBox(uuid):
    '''Create/get a riak bucket for user messages'''
    bname = 'messages_database_%s' % uuid
    bname = str(bname)
    mdb = riakClient.bucket(bname)
    riakClient.create_search_index(bname)
    try:
        mdb.set_properties({'search_index': bname})
    except Exception, e:
        pass
    mdb.enable_search()
    return mdb



class GetMessagesList:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        mdb = getUserMessageBox(user.get('uuid'))
        resp.body = mdb.get_keys()

class GetMessage:
    def on_get(self, req, resp, key):
        user = getUserInfoFromSession(req, resp)
        mdb = getUserMessageBox(user.get('uuid'))
        data = mdb.get(key)
        result = data.data
        result['dtSent'] = data.last_modified
        resp.body = result

class SetMessage:
    def on_post(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        message = get_params(req.stream, False)
        TO = req.session.query(User).filter_by(email=message.get('to')).first()
        FROM = req.session.query(User).filter_by(email=user.get('email')).first()
        _from = user.get('email')
        _from_fn = user.get('firstname')
        _from_ln = user.get('lastname')

        data = {
                'to_s':
                    {
                        'firstname_s':TO.firstname,
                        'lastname_s':TO.lastname,
                        'email_s':TO.email,
                        'id':TO.id,
                    },
                'from_s':
                    {
                        'firstname_s':FROM.firstname,
                        'lastname_s':FROM.lastname,
                        'email_s':FROM.email,
                        'id':FROM.id
                    },
                'target_readed':False,
                'sender_readed':False,
                'attachments':[],
                'body_s':message.get('body'),
                'subject_s':message.get('subject'),
                'folder':'sent',
                'stared': bool(message.get('started')),
                'archived': bool(message.get('archived')),
                'flagged': bool(message.get('flagged'))
        }

        target_data = data.copy()
        target_data['folder'] = 'inbox'
        if not TO or not message.get('subject') or message.get('draft'):
            data['folder'] = 'draft'
            target_data = {}
        if FROM and message.get('body'):
            key = getUUID()
            if data:
                from_mdb = getUserMessageBox(FROM.uuid)
                obj = from_mdb.new(key, data)
                obj.store()
            if target_data:
                to_mdb = getUserMessageBox(TO.uuid)
                tobj = to_mdb.new(key, target_data)
                tobj.store()
            if data:
                resp.body = {'message':data, 'key':key}
            else:
                resp.status = falcon.HTTP_201
        else:
            resp.status = falcon.HTTP_400
            resp.body = {'message':'error', 'info':'subject, to and body needed.'}

class SearchMessages:
    def on_get(self, req, resp, query):
        resp.body = 'not implemented'
