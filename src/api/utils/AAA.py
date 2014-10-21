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
from base64 import encodestring
from urllib import quote_plus, unquote_plus
import falcon
from tasks import send_envelope

def getANewSessionId():
    return str(hmac.HMAC(key=str(uuid.uuid4()), digestmod=hashlib.sha1).hexdigest())


def Authenticate(req, resp, params):
    free_services = ['/api/auth/signup', '/api/auth/login',
                     '/api/things', '/api/auth/activate', '/api/auth/reacticate',
                     '/api/auth/reset']
    sid = req.cookie('session-id')
    ''' Now we need to check if session is available and it's sha1 is in redis'''
    if req.path in free_services or (sid and r.get(hashlib.sha1(sid).hexdigest())):
        print 'i am here'
        ''' Now we need to authorize user!
            NOT IMPLEMENTED YET
        '''
        pass
    else:
        sid = getANewSessionId()
        hashed_sid = hashlib.sha1(sid).hexdigest()
        resp.append_header('Set-Cookie', 'session-id=%s;path=/;max-age=10; HttpOnly' % sid)  # this session is not yet saved
        #resp.status = falcon.HTTP_302
        #next = encodestring(req.path)
        resp.location = '/app/#auth/login/%s' % next
        raise falcon.HTTPUnauthorized('Authentication required',
                          'Please provide authentication headers',
                          href=req.protocol + '://'+ req.headers.get('HOST') + '/app/#auth/login',
                          scheme='Token; UUID')
    #if token != 'rrferl':
    #    raise falcon.HTTPUnauthorized("Authentication Required", "You need to login and have permission!")
    #    return


class Login:
    '''Main login class
    '''
    @falcon.after(commit)
    def on_post(self, req, resp):
        '''Add a user to database'''
        sid = req.cookie('session-id')
        if sid and r.get('fail_'+sid):
            resp.body = {'message': 'error', 'info':'Very Quick! Good, but you need to wait', 'wait':5}
            return
        form = json.loads(req.stream.read())
        target = session.query(User).filter(User.email == form.get('email')).first()
        if not sid:
            sid = getANewSessionId()

        hashed_sid = hashlib.sha1(sid).hexdigest()
        '''
            Here is the smart line! If users tries
            to login again and again, then the same
            cookie will be used
        '''
        resp.set_header('set-cookie', 'session-id=%s; path=/; max-age=5; HttpOnly' % sid)  # this session is not yet saved
        if not target or not target.password == form.get('password'):  # don't tell what's wrong!
            r.incr('fail_'+sid, 1)
            r.expire('fail_' + sid, 60)
            resp.body = {'message':'error', 'info': 'login information is not correct', 'wait':5}
        else:
            if target.active:
                target.lastLogIn = now()
                rem_time = 3600*24
                resp.set_header('set-cookie', 'session-id=%s; path=/; max-age=%s; HttpOnly' % (sid, rem_time))  # this session is not yet saved
                r.incr(hashed_sid, 1)  # add it to redis
                r.expire(hashed_sid, rem_time)
                resp.body = {'message':'success',
                                        'firstname':target.firstname,
                                        'id':target.id}
            else:

                resp.body = {'message':'error',
                             'info':'Please check your email and activate your account',
                             'not_active':True}





        #print email
        #resp.body = 'OK'
class Signup:
    '''Main login class
    '''
    @falcon.after(commit)
    def on_post(self, req, resp):
        sid = req.cookie('session-id')
        if sid and r.get('fail_'+sid):
            resp.body = {'message': 'error', 'info':'You need to wait', 'wait':5}
            return

        host = req.protocol + '://' + req.headers.get('HOST')
        form = json.loads(req.stream.read())
        olduser = session.query(User).filter(User.email == form.get('email')).first()
        if not olduser:
            newuser = User(email=form.get('email'),
                           password=form.get('password'),
                           firstname=form.get('firstname'),
                           lastname=form.get('lastname'),
                           token=str(uuid.uuid4()))

            session.add(newuser)
            #commit(req, resp)



            activation_link = host + '/api/auth/activate?token=' + newuser.token
            send_envelope.delay(form.get('email'), 'Account Activation',
                'Hi <strong>{u}</strong>! Please <a href="{l}">Activate</a> your account.'.format(u=newuser.firstname.title(),
                                    l=activation_link))

            resp.body = {'message': 'success', 'info':'check your activation email'}
        else:
            resp.body = {'message': 'error', 'info':'email address is a registered one'}


class Verify:
    '''Account activation
    '''

    @falcon.after(commit)
    def on_get(self, req, resp):
        token = req.get_param('token')
        target = session.query(User).filter(User.token==token).first()
        if not target:
            m = encodestring('Activation key is expired!')
            resp.status = falcon.HTTP_303
            resp.location = '/app/#auth/reactivate?m=%s'%m
        else:
            new_token = str(uuid.uuid4())
            target.active = True
            target.token = new_token
            resp.status = falcon.HTTP_302
            resp.location = '/app/#auth/login'



class Reactivate:
    '''Account activation
    '''
    def on_post(self, req, resp):
        form = json.loads(req.stream.read())
        target = session.query(User).filter(User.email==form.get('email')).first()
        if target and target.active:
            resp.body = {'message': 'error', 'info':'account is already active', 'not_active':False}
        elif target and not target.active:
            host = req.protocol + '://' + req.headers.get('HOST')
            activation_link = host + '/api/auth/activate?token=' + target.token
            send_envelope.delay(form.get('email'), 'Account ReActivation',
                'Hi <strong>{u}</strong>! Please <a href="{l}">ReActivate</a> your account.'.format(u=target.firstname,
                                    l=activation_link))

            resp.body = {'message': 'success', 'info':'check your reactivation email'}
            return

        else:
            resp.status = falcon.HTTP_202
            resp.body = {'message': 'error', 'info':'email not available'}



class Reset:
    '''Account activation
    '''
    def on_post(self, req, resp):
        pass