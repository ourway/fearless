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
import riak
from uuid import uuid4
import time


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')



def getUserMessageBox(uuid, btype):
    '''Create/get a riak bucket for user messages'''
    bname = 'messages_database_%s' % uuid
    tname = 'mail_%s' % btype
    bname = str(bname)
    tname = str(tname)
    mdb = riakClient.bucket_type(tname).bucket(bname)
    riakClient.create_search_index(bname)
    try:
        mdb.set_properties({'search_index': bname})
        mdb.enable_search()
    except Exception, e:
        pass
    return mdb



class GetMessagesList:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        bfolder = req.get_param('folder') or 'inbox'
        if not bfolder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        mdb = getUserMessageBox(user.get('uuid'), bfolder)
        resp.body = mdb.get_keys()


class GetMessages:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        bfolder = req.get_param('folder') or 'inbox'
        if not bfolder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        mdb = getUserMessageBox(user.get('uuid'), bfolder)
        objects = mdb.get_keys()
        result = []
        for key in objects:
            message = mdb.get(key)
            try:
                mdata = message.data
                mdata['key'] = key
                result.append(mdata)
            except riak.ConflictError:
                message = message.siblings[-1]
                mdata = message.data
                mdata['key'] = key
                result.append(mdata)
                #mdb.delete(key)
            except ValueError:
                mdb.delete(key)
            except TypeError:
                ## message is in wrong format, delete it!!!
                mdb.delete(key)

        resp.body = result


class GetMessage:
    def on_get(self, req, resp, key):
        user = getUserInfoFromSession(req, resp)
        bfolder = req.get_param('folder') or 'inbox'
        mdb = getUserMessageBox(user.get('uuid'), bfolder)
        if not bfolder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        data = mdb.get(key)
        messages = []
        for message in data.siblings:
            result = message.data
            try:
                result['key'] = key
            except TypeError:
                pass
            messages.append(result)
        resp.body = messages

class SetMessage:
    def on_post(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        message = get_params(req.stream, False)
        TO = None
        if message.get('to'):
            TO = req.session.query(User).filter_by(id=message.get('to').get('id')).first()
        FROM = req.session.query(User).filter_by(email=user.get('email')).first()
        _from = user.get('email')
        _from_fn = user.get('firstname')
        _from_ln = user.get('lastname')

        data = {
                'to_s':
                    {
                        'firstname_s':TO.firstname if TO else None,
                        'lastname_s':TO.lastname if TO else None,
                        'email_s':TO.email if TO else None,
                        'id':TO.id if TO else None,
                    },
                'from_s':
                    {
                        'firstname_s':FROM.firstname,
                        'lastname_s':FROM.lastname,
                        'email_s':FROM.email,
                        'id':FROM.id
                    },
                'read':False,
                'attachments':[],
                'body_s':message.get('body'),
                'subject_s':message.get('subject'),
                'folder':'sent',
                'stared': False,
                'flagged': False,
                'datetime': time.time()
        }

        target_data = data.copy()
        bfolder = message.get('folder') or 'sent'
        if not bfolder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        if not TO or not message.get('subject') or message.get('draft'):
            bfolder = 'draft'
            target_data = {}
            data['folder'] = 'draft'
        if FROM and message.get('body'):
            key = getUUID()
            if data:
                from_mdb = getUserMessageBox(FROM.uuid,  bfolder)
                obj = from_mdb.new(key, data)
                obj.store()
            if target_data:
                to_mdb = getUserMessageBox(TO.uuid, 'inbox')
                target_data['folder'] = 'inbox'
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

class DeleteMessage:
    def on_get(self, req, resp, query):
        resp.body = 'not implemented'


class UpdateMessage:
    def on_post(self, req, resp, key):
        options = get_params(req.stream, False)
        folder = options.get('folder')
        message = options.get('message')
        user = getUserInfoFromSession(req, resp)
        mdb = getUserMessageBox(user.get('uuid'),  folder)
        mdb.delete(key)
        obj = mdb.new(key, message)
        obj.store()
        resp.body = {'message':'updated'}

class MoveMessage:
    def on_post(self, req, resp, key):
        options = get_params(req.stream, False)
        from_folder = options.get('from_folder') or req.get_param('from_folder')
        to_folder = options.get('to_folder') or req.get_param('to_folder')
        if not from_folder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        if not to_folder in ['inbox', 'sent', 'draft', 'star', 'archive', 'spam', 'trash']:
            resp.body = falcon.HTTP_400
            return
        if to_folder == from_folder:
            resp.body = falcon.HTTP_201
            return
        user = getUserInfoFromSession(req, resp)
        mdb = getUserMessageBox(user.get('uuid'),  from_folder)
        message =  mdb.get(key)
        try:
            data = message.data
        except riak.ConflictError:
            data = message.siblings[-1].data
        # lets move
        if data:
            target_mdb = getUserMessageBox(user.get('uuid'),  to_folder)
            tobj = target_mdb.new(key, data)
            tobj.store()
            mdb.delete(key)
            resp.body = falcon.HTTP_201
            resp.body = {'message':'MOVED'}
        else:
            resp.status = falcon.HTTP_404
            resp.body = {'message':'Not Found'}
    

