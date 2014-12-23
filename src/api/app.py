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
import cgi
#cgi.maxlen = 10 * 1024 * 1024 # 8Gb
import importlib
from utils.helpers import commit, jsonify, get_params
import urlparse
from urllib import unquote
from string import ascii_uppercase
import ujson as json
from utils.assets import AssetSave, ListAssets, GetAsset, DeleteAsset, CollectionInfo, AddCollection
from utils.reports import Mailer, AddReport
from gevent import wsgi
from models import __all__ as av
from models import *
from sqlalchemy import desc
from datetime import datetime



from sqlalchemy.exc import IntegrityError  # for exception handeling
from utils.AAA import Login, Signup, Authenticate,\
    Verify, Reactivate, Reset, Logout, GetUserInfo, Authorize, \
    getUserInfoFromSession, isAuthorizedTo, GetPermissions, ChangePasswordVerify, \
    ChangePassword, Users, UpdateGroups
from utils.showtime import GetUserShows
from utils.project import GetProjectDetails, GetProjectLatestReport, \
        ListProjects, AddProject, AddTask, ListTasks, GetTask, UpdateTask, \
        DeleteTask, UpdateProject

from utils.sequence import AddSequence



tables = [i for i in av if i[0] in ascii_uppercase]


class ThingsResource:
    #@Authorize('create_collection')
    def on_get(self, req, resp):
        """Handles GET requests"""
        req.env['hooooooo'] = 'gooooooooo'
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        resp.body = "okokokoko"


class DB:

    '''Restfull API for database
    '''

    #@Authorize('see_db')
    def on_get(self, req, resp, **kw):
        banned = ['password', 'token', 'created_on', 'modified_on', 
                  'session_id', 'latest_session_id', 'lastLogIn', 'password2']
        args = req.path.split('/')
        table = args[3]
        u = getUserInfoFromSession(req)
        #if not isAuthorizedTo(u.get('id'), 'see_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        key = req.get_param('key') or 'id'
        listMe = req.get_param('list')
        table = table.title()
        show = req.get_param('show')
        start = req.get_param('s')
        end = req.get_param('e')
        order_by = req.get_param('order_by')
        if not order_by:
            order_by = 'modified_on'

        if start: start = int(start)
        if end: end = int(end)
        if start and not end:
            end = start+10
        if len(args) == 5:
            id = args[4]
            query = 'session.query({t}).filter({t}.{key}=="{id}").order_by(desc({t}.{order}))'.format(
                t=table, id=id, key=key, order=order_by)
            data = eval(query).all()
        else:
            if not show:
                query = 'session.query({t}).order_by(desc({t}.{order}))'.format(t=table, order=order_by)
            else:
                query = 'session.query({t}.{f}).order_by(desc({t}.{order}))'.format(t=table, f=show, order=order_by)
            
            try:
                if start and end:
                    data = eval(query).slice(start, end)
                else:
                    data = eval(query).all()
            except (AttributeError):
                data = None

        field = req.get_param('field')
        if field:
            if field in banned:
                resp.status = falcon.HTTP_403
                resp.body = {'message':'Not Authorized'}
                return
            try:
                if len(args) != 5:
                    data = [eval('i.%s'%field) for i in data]


                elif len(args) == 5:
                    '''/api/db/user/1?field=tasks'''
                    finalResult = []
                    for i in data:
                        #_d = eval('i.%s'%field)
                        _d = getattr(i, field)
                        if isinstance(_d, list):
                            for item in _d:
                                newDataDict = dict()
                                for key in item.__dict__.keys():
                                    value = getattr(item, key)
                                    if isinstance(value, (str, type(None), unicode, int, float, long, datetime)):
                                        newDataDict[key] = value
                                finalResult.append(newDataDict)
                        else:
                            newDataDict = dict()
                            for key in _d.__dict__.keys():
                                value = getattr(_d, key)
                                if isinstance(value, (str, type(None), unicode, int, float, long, datetime)):
                                    newDataDict[key] = value

                    data = finalResult

                            

            except AttributeError, e:
                print e
                raise falcon.HTTPBadRequest('Bad Request', 'The requested field is not available for database')


            resp.body = data
            return


        try:
            #data = repr(data)
            d = json.loads(data)
            if d and isinstance(d, dict):
                for i in banned:
                    if d.get(i):
                        del(d[i])

            if d and isinstance(d, list):
                for each in d:
                    if isinstance(each, dict):
                        for i in banned:
                            if each.get(i):
                                del(each[i])

            resp.body = d
        except (TypeError, ValueError):
            resp.body = data

        if len(args)==5 and len(data)==1 and not listMe:
            resp.body = data[0]
        # Ok, We have an id

    @falcon.after(commit)
    def on_put(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        u = getUserInfoFromSession(req)
        #if not isAuthorizedTo(u.get('id'), 'create_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        query_params = get_params(req.stream, flat=False)
        insert_cmd = '{t}()'.format(t=table)
        new = eval(insert_cmd)
        for i in query_params:
            setattr(new, i, query_params.get(i))
        resp.status = falcon.HTTP_201
        session.add(new)
        data = repr(new)
        resp.body = json.dumps(json.loads(data))
        # commit()


    @falcon.after(commit)
    def on_post(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        #u = getUserInfoFromSession(req)
        #if not isAuthorizedTo(u.get('id'), 'update_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        if len(args)<5:
            resp.status = falcon.HTTP_400
            return
        id = args[4]
        # lets get the table data
        query = 'session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query).first()
        ##
        query_params = get_params(req.stream, flat=False)
        updated_values = [];
        for key in query_params:
            key = str(key)
            value = query_params[key]
            if isinstance(value, (int, str, unicode, float)) and hasattr(result, key):
                setattr(result, key, value)
                updated_values.append(key)

        #if result.update(query_params):
        resp.status = falcon.HTTP_202
        resp.body = {'message':'updated', 'info':updated_values}
        #query = 'result({q})'.format(q=query_params)
        # print eval(query)

    @falcon.after(commit)
    def on_delete(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        #u = getUserInfoFromSession(req)
        #if not isAuthorizedTo(u.get('id'), 'delete_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        if len(args)<5:
            resp.status = falcon.HTTP_400
            return
        id = args[4]
        # lets get the table data
        query = 'session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query).all()
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
app.add_route('/api/users', Users())
app.add_route('/api/auth/login', Login())
app.add_route('/api/auth/signup', Signup())
app.add_route('/api/auth/activate', Verify())
app.add_route('/api/auth/reactivate', Reactivate())
app.add_route('/api/auth/reset', Reset())
app.add_route('/api/auth/logout', Logout())
app.add_route('/api/auth/getUserInfo', GetUserInfo())
app.add_route('/api/auth/permissions/{userId}', GetPermissions())
app.add_route('/api/auth/changepasswordverify', ChangePasswordVerify())
app.add_route('/api/auth/changepassword', ChangePassword())
app.add_route('/api/asset/save/{repo}', AssetSave())
app.add_route('/api/asset', ListAssets())
app.add_route('/api/asset/{key}', GetAsset())
app.add_route('/api/asset/delete/{id}', DeleteAsset())
app.add_route('/api/showtime/{userid}', GetUserShows())
app.add_route('/api/project', ListProjects())
app.add_route('/api/project/add', AddProject())
app.add_route('/api/project/update/{projId}', UpdateProject())
app.add_route('/api/project/get/{id}', GetProjectDetails())
app.add_route('/api/project/report/{id}', GetProjectLatestReport())
app.add_route('/api/collection/{collectionId}', CollectionInfo())
app.add_route('/api/collection/add', AddCollection())
app.add_route('/api/task/add/{projId}', AddTask())
app.add_route('/api/task/list/{projId}', ListTasks())
app.add_route('/api/task/{taskId}', GetTask())
app.add_route('/api/task/update/{taskId}', UpdateTask())
app.add_route('/api/task/delete/{taskId}', DeleteTask())
app.add_route('/api/sequence/add/{projId}', AddSequence())
app.add_route('/api/sendmail', Mailer())
app.add_route('/api/report', AddReport())
app.add_route('/api/user/{userId}/groups', UpdateGroups())


if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    #from werkzeug import run_simple
    #run_simple('0.0.0.0', 5002, app, use_debugger=True, use_reloader=True)
    wsgi.WSGIServer(('127.0.0.1', 5002), app).serve_forever()
