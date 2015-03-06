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


from flib.models import User, Group, Role, r, now  # r is redis
from flib.utils.helpers import get_ip, get_params
import ujson as json
import hmac
import uuid
import hashlib
from flib.utils.general import setup_logger
from base64 import encodestring, decodestring
from urllib import quote_plus, unquote_plus
import falcon
from flib.tasks import send_envelope
from functools import wraps


logger = setup_logger('auth', 'authentication.log')


def getANewSessionId():
    return str(hmac.HMAC(key=str(uuid.uuid4()), digestmod=hashlib.sha1).hexdigest())


def Authorize(action):
    def request_checked(func):
        def _f(self, req, resp, *args, **kw):
            u = getUserInfoFromSession(req, resp)
            if isAuthorizedTo(req, u.get('id'), action):
                return func(self, req, resp, *args, **kw)
            else:
                raise falcon.HTTPUnauthorized(
                    'Not Authorized', 'Permission Denied')
        return _f
    return request_checked


def Authenticate(req, resp, params):
    '''

    :param req:
    :param resp:
    :param params:
    :return:

    usage:
        using curl or httpie:
            http "http://127.0.0.1:5003/api/db/user" --auth rodmena@me.com:password
        using requests:
            ...
        using urllib2:
            ...

    '''
    # return
    ip = req.env.get('HTTP_X_FORWARDED_FOR') or req.env.get('REMOTE_ADDR')
    free_services = ['/api/auth/signup', '/api/auth/login',
                     '/api/things', '/api/auth/activate', '/api/auth/reactivate',
                     '/api/auth/reset', '/api/auth/logout', '/api/auth/getUserInfo',
                     '/api/auth/changepasswordverify', '/api/auth/changepassword', '/api/test_upload']

    sid = req.cookie('session-id')
    if sid:
        sid_digest = hashlib.sha1(sid).hexdigest()
    ip_digest = hashlib.sha1(ip).hexdigest()
    ''' Now we need to check if session is available and it's sha1 is in redis'''
    if req.path in free_services or '/api/note' in req.path or (sid and r.get(sid_digest)):
        ''' User can access 1000 api calls per minute (for now! NOTE)'''
        api_count_key = ip_digest + '_access_count'
        access_count = r.get(api_count_key)
        if not access_count:
            '''probabaly acceess count expired, lets create one and let user in'''
            r.set(api_count_key, 1)
            r.expire(api_count_key, 60)
        # not more than 1000 requests per second!  its fair
        elif int(access_count) <= 1000:
            r.incr(api_count_key, 1)
        elif not '/api/test_upload' in req.path and not '/api/asset/save' in req.path:
            message = 'Too many api access in short amount of time'
            raise falcon.HTTPUnauthorized('Authentication required', message)

    else:
        auth_header = req.headers.get('AUTHORIZATION')
        if auth_header:
            auth_header_parts = auth_header.split()
            if len(auth_header_parts) == 2:
                auth_mode, auth_64 = auth_header_parts
                # ok, we need to check it
                if auth_mode and auth_64 and auth_mode == 'Basic':
                    username, password = decodestring(auth_64).split(':')
                    user = req.session.query(User).filter(
                        User.email == username).first()
                    if user and user.password == password:
                        logger.info(
                            '{ip}|{u} accessed with Basic Auth for API use"'.format(u=user.email, ip=ip))
                        return  # FREE PASS TO GO
                    else:
                        logger.info(
                            'User "{u}" provided wrong Basic Auth for API use"'.format(u=username))
                        message = 'Wrong Info'
                else:
                    message = 'Incorrect Auth header. Must be Basic'
            else:
                message = 'Wrong Auth header formatting'
        else:
            message = 'You need to provide Basic Auth header to authenticate'

        sid = getANewSessionId()
        hashed_sid = hashlib.sha1(sid).hexdigest()
        # this session is not yet saved
        resp.append_header(
            'Set-Cookie', 'session-id=%s;path=/;max-age=10; HttpOnly' % sid)
        #resp.status = falcon.HTTP_302
        #next = encodestring(req.path)
        resp.location = '/app/#auth/login/%s' % next
        raise falcon.HTTPUnauthorized('Authentication required',
                                      message,
                                      href=req.protocol + '://' +
                                      req.headers.get(
                                          'HOST') + '/app/#auth/login',
                                      scheme='Token; UUID')
    # if token != 'rrferl':
    #    raise falcon.HTTPUnauthorized("Authentication Required", "You need to login and have permission!")
    #    return


class Login:

    '''Main login class
    '''

    def on_post(self, req, resp):
        '''Add a user to database'''
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        sid = req.cookie('session-id')
        if sid and r.get('fail_' + sid):
            resp.body = {
                'message': 'error', 'info': 'Very Quick! Good, but you need to wait', 'wait': 5}
            return
        form = json.loads(req.stream.read())
        email = form.get('email')
        if email:
            email = email.lower()
        target = req.session.query(User).filter(
            User.email == email).first()
        if not sid:
            sid = getANewSessionId()

        hashed_sid = hashlib.sha1(sid).hexdigest()
        '''
            Here is the smart line! If users tries
            to login again and again, then the same
            cookie will be used
        '''
        resp.append_header('set-cookie', 'session-id=%s; path=/; max-age=5; HttpOnly' %
                           sid)  # this session is not yet saved
        # don't tell what's wrong!
        if not target or not target.password == form.get('password'):
            r.incr('fail_' + sid, 1)
            r.expire('fail_' + sid, 60)
            logger.warning('{ip}|Wrong information provided'.format(ip=ip))
            resp.body = {
                'message': 'error', 'info': 'login information is not correct', 'wait': 5}
        else:
            if target.active:
                target.lastLogIn = now()
                rem_time = 3600 * 24
                # this session is not yet saved

                groups = ','.join([i.name for i in target.grps])
                resp.append_header(
                    'set-cookie', 'userid=%s; path=/; max-age=%s' % (str(target.id), rem_time))
                resp.append_header(
                    'set-cookie', 'groups=%s; path=/; max-age=%s' % (str(groups), rem_time))
                resp.append_header('set-cookie', 'username=%s; path=/; max-age=%s' %
                                   (str(target.firstname or target.alias), rem_time))
                resp.append_header(
                    'set-cookie', 'session-id=%s; path=/; max-age=%s; HttpOnly' % (sid, rem_time))

                target.latest_session_id = hashed_sid
                r.incr(hashed_sid, 1)  # add it to redis
                r.expire(hashed_sid, rem_time)

                logger.info(
                    '{ip}|"{u}" loggin in from web"'.format(u=target.email, ip=ip))
                resp.body = {
                    'message': 'success',
                    'firstname': target.firstname,
                    'id': target.id,
                    'avatar': target.avatar,
                    'groups': [i.name for i in target.grps]
                }
            else:

                logger.warning('{ip}|{u} tried to login from web without activation"'.format(
                    u=target.email, ip=ip))
                resp.body = {'message': 'warning',
                             'info': 'Please check your email and activate your account',
                             'not_active': True}

        # print email
        #resp.body = 'OK'


class Signup:

    '''Main login class
    '''

    def on_post(self, req, resp):
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        sid = req.cookie('session-id')
        if sid and r.get('fail_' + sid):
            resp.body = {
                'message': 'error', 'info': 'You need to wait', 'wait': 5}
            return

        host = req.protocol + '://' + req.headers.get('HOST')
        form = json.loads(req.stream.read())
        email = form.get('email')
        if email:
            email = email.lower()
        olduser = req.session.query(User).filter(
            User.email == email).first()
        if not olduser:
            newuser = User(email=email,
                           password=form.get('password'),
                           firstname=form.get('firstname'),
                           lastname=form.get('lastname'),
                           token=str(uuid.uuid4()))

            req.session.add(newuser)
            oldUsersCount = req.session.query(User).count()
            if oldUsersCount == 1:
                newuser.groups.append('admin')

            activation_link = host + \
                '/api/auth/activate?token=' + newuser.token
            send_envelope.delay(email, [], [], 'Account Activation',
                                'Hi <strong>{u}</strong>! Please <a class="btn-primary" href="{l}">Activate your account</a>.'.format(u=newuser.firstname.title(),
                                                                                                                                      l=activation_link))

            logger.info(
                '{ip}|Signed up for {u}'.format(ip=ip, u=newuser.email))
            resp.body = {
                'message': 'success', 'info': 'check your activation email'}
        else:
            logger.warning('{ip}|Tried to sign up for {u} which is already registered'.format(
                ip=ip, u=olduser.email))
            resp.body = {
                'message': 'error', 'info': 'email address is a registered one'}


class Verify:

    '''Account activation
    '''

    def on_get(self, req, resp):

        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        token = req.get_param('token')
        target = req.session.query(User).filter(User.token == token).first()
        if not target:
            logger.warning(
                '{ip}|Entered an expired activation key'.format(ip=ip))
            m = encodestring('Activation key is expired!')
            resp.status = falcon.HTTP_303
            resp.location = '/app/#auth/reactivate?m=%s' % m
        else:
            new_token = str(uuid.uuid4())
            target.active = True
            target.token = new_token
            logger.info('{ip}|Verified an activation key'.format(ip=ip))
            resp.status = falcon.HTTP_302
            m = encodestring('Welcome!  Successfully Activated.')
            resp.location = '/app/#auth/login?m=%s' % m


class Reactivate:

    '''Account activation
    '''

    def on_post(self, req, resp):
        sid = req.cookie('session-id')
        if sid and r.get('reactivation_%s' % sid):
            resp.body = {'message': 'error', 'info': 'Please wait 5 seconds...',
                         'not_active': False, 'wait': 5}
            return

        if not sid:
            sid = getANewSessionId()
            # this session is temprary
            resp.set_header(
                'set-cookie', 'session-id=%s; path=/; max-age=%s; HttpOnly' % (sid, 5))
        r.incr('reactivation_' + sid, 1)
        r.expire('reactivation_' + sid, 60)
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        form = json.loads(req.stream.read())
        target = req.session.query(User).filter(
            User.email == form.get('email')).first()
        if target and target.active:
            resp.body = {
                'message': 'error', 'info': 'account is already active', 'not_active': False}
            logger.warning('{ip}|Tried to reactivate {u} which is already activated!'.format(
                ip=ip, u=target.email))
        elif target and not target.active:
            host = req.protocol + '://' + req.headers.get('HOST')
            activation_link = host + '/api/auth/activate?token=' + target.token
            send_envelope.delay(form.get('email'), [], [], 'Account ReActivation',
                                'Hi <strong>{u}</strong>! Please <a href="{l}">ReActivate</a> your account.'.format(u=target.firstname,
                                                                                                                    l=activation_link))

            logger.info(
                '{ip}|requested reactivation key for {u}'.format(ip=ip, u=target.email))
            resp.body = {
                'message': 'success', 'info': 'check your reactivation email'}
            #resp.status = falcon.HTTP_302
            #m = encodestring('Check your email for activation key.')
            # resp.location = '/app/#auth/login?m=%s'%m
            # return

        else:
            resp.status = falcon.HTTP_202
            logger.warning(
                '{ip}|requested reactivation key for not existed account'.format(ip=ip))
            resp.body = {'message': 'error', 'info': 'email not available'}


class ChangePasswordVerify:

    '''Account password token
    '''

    def on_get(self, req, resp):
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        token = req.get_param('token')
        target = req.session.query(User).filter(User.token == token).first()
        if not target:
            logger.warning(
                '{ip}|Entered an expired reset key'.format(ip=ip))
            m = encodestring('reset key is expired!')
            resp.status = falcon.HTTP_303
            resp.location = '/app/#auth/login?m=%s' % m
        else:
            new_token = str(uuid.uuid4())
            target.active = True
            target.token = new_token
            logger.info('{ip}|Verified a reset key'.format(ip=ip))
            resp.status = falcon.HTTP_302
            m = encodestring(
                'hey %s! You can reset your password here' % target.firstname)
            resp.location = '/app/#auth/changepassword/%s' % new_token


class ChangePassword:

    '''Account pass change
    '''

    def on_post(self, req, resp):
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        form = json.loads(req.stream.read())
        token = req.get_param('token')
        pass1 = form.get('password')
        pass2 = form.get('password2')
        target = req.session.query(User).filter(User.token == token).first()
        if target and pass1 and pass2 and len(pass1) > 5 and pass1 == pass2:
            new_token = str(uuid.uuid4())
            target.token = new_token
            target.password = pass1
            resp.body = {'message': 'password changed'}
        else:
            resp.body = {'message': 'error in password change'}


class Reset:

    '''Account activation
    '''

    def on_post(self, req, resp):
        sid = req.cookie('session-id')
        if sid and r.get('reactivation_%s' % sid):
            resp.body = {'message': 'error', 'info': 'Please wait 5 seconds...',
                         'not_active': False, 'wait': 5}
            return

        if not sid:
            sid = getANewSessionId()
            # this session is temprary
            resp.set_header(
                'set-cookie', 'session-id=%s; path=/; max-age=%s; HttpOnly' % (sid, 5))
        r.incr('reactivation_' + sid, 1)
        r.expire('reactivation_' + sid, 60)
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        form = json.loads(req.stream.read())
        target = req.session.query(User).filter(
            User.email == form.get('email')).first()
        if target:
            host = req.protocol + '://' + req.headers.get('HOST')
            reset_link = host + \
                '/api/auth/changepasswordverify?token=' + target.token
            send_envelope.delay(form.get('email'), [], [],  'Account Password Reset',
                                'Hi <strong>{u}</strong>! <a href="{l}">reset</a> your account password.'.format(u=target.firstname,
                                                                                                                 l=reset_link))
            resp.body = {'message': 'reset key sent'}


class Logout:

    '''Account activation
    '''

    def on_post(self, req, resp):
        ip = req.env.get('HTTP_X_FORWARDED_FOR')
        sid = req.cookie('session-id')
        if sid:
            hashed_sid = hashlib.sha1(sid).hexdigest()
            target = req.session.query(User).filter(
                User.latest_session_id == hashed_sid).first()
            if not target:
                logger.warning(
                    '{ip}|tried to logout of an invalid session'.format(ip=ip))
            else:
                logger.info('{ip}|logged out'.format(ip=ip))
                target.latest_session_id = None

            resp.append_header(
                'set-cookie', 'username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/')
            resp.append_header(
                'set-cookie', 'userid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/')
            resp.body = r.delete(hashed_sid)


def getUserInfoFromSession(req, resp):
    sid = req.cookie('session-id')
    if sid:
        hashed_sid = hashlib.sha1(sid).hexdigest()
        target = req.session.query(User).filter(
            User.latest_session_id == hashed_sid).first()
        if target:
            return {'email': target.email, 'alias': target.alias, 'firstname': target.firstname, 'uuid': target.uuid,
                    'lastname': target.lastname, 'id': target.id, 'server': {'name': 'Fearless API', 'ip': get_ip()}}

        else:

            resp.append_header(
                'set-cookie', 'username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/')
            resp.append_header(
                'set-cookie', 'userid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/')
            r.delete(hashed_sid)
            raise falcon.HTTPUnauthorized(
                'Not Authorized', 'You need to login before using Fearless API')

    return {'message': 'ERROR'}


class GetUserInfo:
    #@falcon.after(commit)

    def on_post(self, req, resp):
        resp.body = getUserInfoFromSession(req, resp)


class GetPermissions:

    def on_get(self, req, resp, userId):
        target = req.session.query(User).filter(User.id == int(userId)).first()
        resp.body = [i.rls for i in target.grps]


def isAuthorizedTo(req, userId, actionName):
    '''authorization function.  It should find a role or group in user database with same name'''
    target = req.session.query(User).filter(User.id == userId).first()
    if not target:
        return

    if target.id == 1:  # first user has access to everything
        return True

    for userGroup in target.grps:  # grps is access to gourp objects
        if actionName.lower() == userGroup.name.lower():
            return True
        for role in userGroup.rls:  # rls is access to role object
            if actionName.lower() == role.name.lower():
                return True


class Users:

    def on_get(self, req, resp, **kw):

        target = req.session.query(User).all()
        data = [{'firstname': user.lastname, 'lastname': user.firstname,
                 'fullname': user.fullname, 'id': user.id} for user in target]
        resp.body = data


class UpdateGroups:

    def on_get(self, req, resp, userId, **kw):
        pass

    def on_post(self, req, resp, userId):
        target = req.session.query(User).filter_by(id=int(userId)).first()
        data = get_params(req.stream, False)
        added = []
        if data.get('groups'):
            target.grps = []
            target.groups = [i.get('name') for i in data.get('groups')]
            if 'guests' in target.groups and 'users' not in target.groups:
                target.groups.append('users')

            if target.id == 1 and not 'admin' in target.groups:
                target.groups.append('admin')

            resp.status = falcon.HTTP_202
            resp.body = {'message': 'OK'}


class UpdateDepartements:

    def on_get(self, req, resp, userId, **kw):
        pass

    def on_post(self, req, resp, userId):
        target = req.session.query(User).filter_by(id=int(userId)).first()
        data = get_params(req.stream, False)
        if data.get('departements'):
            target.dps = []
            target.departements = [i.get('name')
                                   for i in data.get('departements')]

            resp.status = falcon.HTTP_202
            resp.body = {'message': 'OK'}


class UpdateExpertise:

    def on_get(self, req, resp, userId, **kw):
        pass

    def on_post(self, req, resp, userId):
        target = req.session.query(User).filter_by(id=int(userId)).first()
        data = get_params(req.stream, False)
        if data.get('expertise'):
            target.exps = []
            target.expertise = [i.get('name') for i in data.get('expertise')]

            resp.status = falcon.HTTP_202
            resp.body = {'message': 'OK'}
