#!../../pyenv/bin/python
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

#from gevent import monkey; monkey.patch_all()
from falcon_patch import falcon
import importlib
from utils.helpers import commit, jsonify
import urlparse
from urllib import unquote
from string import ascii_uppercase
import ujson as json
from utils.assets import AssetSave, ListAssets, GetAsset
from utils.reports import Mailer
from gevent import wsgi
from models import __all__ as av
from models import *
import uwsgi

from sqlalchemy.exc import IntegrityError  # for exception handeling
from utils.AAA import Login, Signup, Authenticate,\
    Verify, Reactivate, Reset, Logout, GetUserInfo
from utils.showtime import GetUserShows

tables = [i for i in av if i[0] in ascii_uppercase]


def get_params(stream, flat=True):
    '''Return a string out of url params for query
    '''
    if not stream:
        return {}
    data = stream.read()
    if not data:
        return {}
    stream = json.loads(data)
    if not flat:
        return stream
    l = ','.join(['%s="%s"' % (i, stream[i]) for i in stream])
    return l


class ThingsResource:

    def on_get(self, req, resp):
        """Handles GET requests"""
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        resp.body = "ok"


class DB:

    '''Restfull API for database
    '''

    def on_get(self, req, resp, **kw):

        args = req.path.split('/')
        table = args[3].title()
        key = req.get_param('key') or 'id'

        if len(args) == 5:
            id = args[4]
            query = 'session.query({t}).filter({t}.{key}=="{id}")'.format(
                t=table, id=id, key=key)

            data = eval(query).first()
        else:
            query = 'session.query({t})'.format(t=table)
            data = eval(query).all()


        field = req.get_param('field')
        if field and len(args)==5:
            try:
                data = eval('data.%s'%field)
            except AttributeError:
                raise falcon.HTTPBadRequest('Bad Request', 'The requested field is not available for database')
            resp.body = data
            return

        try:
            data = repr(data)
            resp.body = json.loads(data)
        except (TypeError, ValueError):
            resp.body = data
        # Ok, We have an id

    @falcon.after(commit)
    def on_put(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        query_params = get_params(req.stream)
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
    def on_post(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        if len(args)<5:
            resp.status = falcon.HTTP_400
            return
        id = args[4]
        # lets get the table data
        query = 'session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query)
        ##
        query_params = get_params(req.stream, flat=False)
        if result.update(query_params):
            resp.status = falcon.HTTP_202
            resp.body = {'message':'updated'}
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
#app = falcon.API()
app = falcon.API(before=[Authenticate], after=[jsonify])
things = ThingsResource()

########################################################
for table in tables:
    app.add_route('/api/db/{t}'.format(t=table), DB())
    app.add_route('/api/db/%s/{id}' % table, DB())
#######################################################

# things will handle all requests to the '/things' URL path
app.add_route('/api/things', things)
app.add_route('/api/auth/login', Login())
app.add_route('/api/auth/signup', Signup())
app.add_route('/api/auth/activate', Verify())
app.add_route('/api/auth/reactivate', Reactivate())
app.add_route('/api/auth/reset', Reset())
app.add_route('/api/auth/logout', Logout())
app.add_route('/api/auth/getUserInfo', GetUserInfo())
app.add_route('/api/asset/save/{repo}', AssetSave())
app.add_route('/api/asset', ListAssets())
app.add_route('/api/asset/{key}', GetAsset())
app.add_route('/api/showtime/{userid}', GetUserShows())
app.add_route('/api/sendmail', Mailer())


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    from werkzeug import run_simple
    run_simple('0.0.0.0', 5004, app, use_debugger=True, use_reloader=True)
    #wsgi.WSGIServer(('127.0.0.1', 5004), app).serve_forever()
