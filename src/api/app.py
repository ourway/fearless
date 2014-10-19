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


from falcon_patch import falcon
import importlib
import urlparse
from urllib2 import quote, unquote
from string import ascii_uppercase
import ujson as json
import redis
import hashlib
import re
#from utils.assets import AssetSave, ListAssets, GetAsset

from models import __all__ as av
from models import *
from sqlalchemy.exc import IntegrityError  # for exception handeling
from utils.AAA import login

tables = [i for i in av if i[0] in ascii_uppercase]
r = redis.StrictRedis(host='localhost', port=6379, db=3)  # db number 1 and 2 are for celery




def get_cookie(cookiename, raw):
    x = re.findall(re.compile(r'[; ]*'+ cookiename + r'=([\w " \. = \d &]+)'), raw)
    if x:
        return x[0]

def get_params(url, flat=True):
    '''Return a string out of url params for query
    '''
    urlinfo = urlparse.urlparse(url)
    params = urlparse.parse_qs(urlinfo.query)
    for param in params:
        params[param] = params[param][0]
    if not flat:
        return params
    l = ','.join(['%s="%s"' % (i, params[i]) for i in params])
    return l


def commit(req, resp):
    try:
        session.commit()
    except IntegrityError, e:
        session.rollback()
        resp.status = falcon.HTTP_400
        resp.body = json.dumps(e)

def getANewSessionId():
    import hmac
    import uuid
    return str(hmac.HMAC(key=str(uuid.uuid4()), digestmod=hashlib.sha1).hexdigest())

def authenticate(req, resp, params):
    free_services = ['/api/auth/signup', '/api/auth/signin', '/api/things']
    path = req.relative_uri
    raw = req.headers.get('COOKIE')
    if not raw:
        session = None
    else:
        session = get_cookie('session-id', raw)

    ''' Now we need to check if session is available and it's sha1 is in redis'''
    if path in free_services or (session and r.get(hashlib.sha1(session).hexdigest())):
        ''' Now we need to authorize user!
            NOT IMPLEMENTED YET
        '''
        pass
    else:
        session = getANewSessionId()
        hashed_session = hashlib.sha1(session).hexdigest()
        resp.append_header('set-cookie', 'session-id=%s;path=/;max-age=10' % session)  # this session is not yet saved
        resp.status = falcon.HTTP_302
        next = quote(path)
        resp.location = '/app/#auth/login?next=%s' % next

    #if token != 'rrferl':
    #    raise falcon.HTTPUnauthorized("Authentication Required", "You need to login and have permission!")
    #    return

class ThingsResource:

    def on_get(self, req, resp):
        """Handles GET requests"""
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        resp.body = "ok"


class DB:
    '''Restfull API for database
    '''

    def on_get(self, req, resp):
        args = req.path.split('/')
        table = args[3].title()
        if len(args) == 5:
            id = args[4]
            query = 'session.query({t}).filter({t}.id=={id})'.format(
                t=table, id=int(id))
            data = eval(query).first()
        else:
            query = 'session.query({t})'.format(t=table)
            data = eval(query).all()


        data = repr(data)
        resp.body = json.dumps(json.loads(data))
        # Ok, We have an id

    @falcon.after(commit)
    def on_put(self, req, resp):
        args = req.path.split('/')
        table = args[3].title()
        query_params = get_params(req.uri)
        insert_cmd = '{t}({q})'.format(t=table, q=query_params)
        try:
            new = eval(insert_cmd)
            resp.status = falcon.HTTP_201
            session.add(new)
            data = repr(new)
            resp.body = json.dumps(json.loads(data))
        except TypeError, e:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps(e)
        # commit()

    @falcon.after(commit)
    def on_patch(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        id = args[4]
        # lets get the table data
        query = 'session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query)
        ##
        query_params = get_params(req.uri, flat=False)
        result.update(query_params)
        resp.status = falcon.HTTP_202
        #query = 'result({q})'.format(q=query_params)
        # print eval(query)

    @falcon.after(commit)
    def on_delete(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        id = args[4]
        # lets get the table data
        query = 'session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query).first()
        ##
        session.delete(result)
        resp.status = falcon.HTTP_202
        #query = 'result({q})'.format(q=query_params)
        # print eval(query)


# falcon.API instances are callable WSGI apps
app = falcon.API(before=[authenticate])
things = ThingsResource()

########################################################
for table in tables:
    app.add_route('/api/db/{t}'.format(t=table), DB() )
    app.add_route('/api/db/%s/{id}' % table, DB())
#######################################################

# things will handle all requests to the '/things' URL path
app.add_route('/api/things', things)
app.add_route('/api/auth/login', login() )
#app.add_route('/api/asset/save/{user}/{repo}', AssetSave())
#app.add_route('/api/asset', ListAssets())
#app.add_route('/api/asset/{key}', GetAsset())


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from werkzeug import run_simple
    run_simple('0.0.0.0', 5002, app, use_debugger=True, use_reloader=True)
