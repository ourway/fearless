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
from model import getdb
db=getdb()

def clean(req, resp, *kw):
    #print kw
    #print dir(db)
    db.commit()
    #db.close()


class Login(object):
    def on_post(self, req, resp, **kw):
        '''Query a user login'''
        data = {'message':False}
        stream = req.stream.read()
        resp.status = falcon.HTTP_400
        if stream:
            resp.status = falcon.HTTP_200
            params = ujson.loads(stream)
            email = params.get('email')
            password = params.get('password')
            if email == 'rodmena@me.com' and password == 'rrferl':
                data = {'message':True, 'id':1, 'first_name':'farsheed'}
        else:
            data['info'] = 'Need to post from a FORM in POST method'

        
        resp.body=ujson.dumps(data)





class Register(object):
    @falcon.after(clean)
    def on_post(self, req, resp, **kw):
        '''Query a user login'''
        params = ujson.loads(req.stream.read())
        data = {'message':False}
        email = params.get('email')
        password = params.get('password')
        if email and email_validator(email) and password:  ## Ok, Email is valid
            pswd = hashlib.sha256(password).hexdigest()  ## lets create a password
        
        resp.body=ujson.dumps(data)

class Recover(object):
    def on_post(self, req, resp, **kw):
        '''Query a user login'''
        params = ujson.loads(req.stream.read())
        data = {'message':False}
        resp.body=ujson.dumps(data)


