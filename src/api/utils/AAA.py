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

#import sys, os
#sys.path.append(os.path.join(os.path.dirname(__file__), '../'))


from models import User, Group, Rule, session, r, now # r is redis
from helpers import commit
import ujson as json
import hmac
import uuid
import hashlib
from urllib2 import quote, unquote
import falcon
from tasks import send_envelope

def getANewSessionId():
    return str(hmac.HMAC(key=str(uuid.uuid4()), digestmod=hashlib.sha1).hexdigest())


def authenticate(req, resp, params):
    free_services = ['/api/auth/signup', '/api/auth/login', '/api/things']
    path = req.relative_uri
    print path
    sid = req.cookie('session-id')
    req.cookie('heyyy')

    ''' Now we need to check if session is available and it's sha1 is in redis'''
    if path in free_services or (sid and r.get(hashlib.sha1(sid).hexdigest())):
        ''' Now we need to authorize user!
            NOT IMPLEMENTED YET
        '''
        pass
    else:
        sid = getANewSessionId()
        hashed_sid = hashlib.sha1(sid).hexdigest()
        resp.append_header('set-cookie', 'session-id=%s;path=/;max-age=10' % sid)  # this session is not yet saved
        resp.status = falcon.HTTP_302
        next = quote(path)
        resp.location = '/app/#auth/login?next=%s' % next

    #if token != 'rrferl':
    #    raise falcon.HTTPUnauthorized("Authentication Required", "You need to login and have permission!")
    #    return


class login:
    '''Main login class
    '''
    @falcon.after(commit)
    def on_post(self, req, resp):
        '''Add a user to database'''
        sid = req.cookie('session-id')
        if sid and r.get('fail_'+sid):
            resp.body = json.dumps({'message': 'error', 'info':'You need to wait', 'wait':5})
            return
        form = json.loads(req.stream.read())
        target = session.query(User).filter(User.email == form.get('email')).first()
        if not sid:
            sid = getANewSessionId()

        '''
            Here is the smart line! If users tries
            to login again and again, then the same
            cookie will be used
        '''
        resp.append_header('set-cookie', 'session-id=%s;path=/;max-age=5' % sid)  # this session is not yet saved
        if not target or not target.password == password:  # don't tell what's wrong!
            r.incr('fail_'+sid, 1)
            resp.body = json.dumps({'message':'error', 'info': 'login information is not correct', 'wait':2})
        else:

            target.lastLogIn = now()
            resp.body = json.dumps({'message':'sucess',
                                    'firstname':target.firstname,
                                    'id':target.id})



        #print email
        #resp.body = 'OK'
class signup:
    '''Main login class
    '''
    @falcon.after(commit)
    def on_post(self, req, resp):
        sid = req.cookie('session-id')
        if sid and r.get('fail_'+sid):
            resp.body = json.dumps({'message': 'error', 'info':'You need to wait', 'wait':5})
            return


        form = json.loads(req.stream.read())

        if not session.query(User).filter(User.email == form.get('email')).first():
            newuser = User(email=form.get('email'),
                           password=form.get('password'),
                           firstname=form.get('firstname'),
                           lastname=form.get('lastname'))
            session.add(newuser)
            commit(req, resp)

            send_envelope.delay(form.get('email'), 'Account Activation', 'your acount is here')
            resp.body = json.dumps({'message': 'success', 'info':'check your activation email'})



        else:
            resp.body = json.dumps({'message': 'error', 'info':'email already available'})
            return



