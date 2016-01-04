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

#from gevent import monkey;monkey.patch_all()
import sys
import os
current_path = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.dirname(current_path)))

from flib.falcon_patch import falcon
import cgi
# cgi.maxlen = 10 * 1024 * 1024 # 8Gb
import importlib
from flib.utils.helpers import commit, jsonify, get_params
from flib.utils.documents import SetNote, GetNote, SearchNote
import urlparse
from urllib import unquote, quote
from string import ascii_uppercase
from sqlalchemy.ext.serializer import loads, dumps
from flib.utils.assets import AssetCheckout, AssetSave, ListAssets, GetAsset, DeleteAsset, CollectionInfo, AddCollection, TestUpload, ZipCollection
from utils.messages import GetMessagesList, GetMessages, GetMessage, SetMessage, \
    SearchMessages, MoveMessage, DeleteMessage, UpdateMessage
from flib.utils.reports import Mailer, AddReport, UserReports, GetUserLatestReports

from utils.comments import AddComment
from utils import grid
from flib.models import __all__ as av
from flib.models import *
from sqlalchemy import desc, asc
from datetime import datetime

from flib.models.db import Session  # scopped session

from sqlalchemy.exc import IntegrityError  # for exception handeling
from flib.utils.AAA import Login, Signup, Authenticate,\
    Verify, Reactivate, Reset, Logout, GetUserInfo, Authorize, \
    getUserInfoFromSession, isAuthorizedTo, GetPermissions, ChangePasswordVerify, \
    ChangePassword, Users, UpdateGroups, UpdateDepartements, UpdateExpertise
from flib.utils.showtime import GetUserShows
from flib.utils.project import GetProjectDetails, GetProjectLatestReport, \
    ListProjects, AddProject, AddTask, ListTasks, GetTask, UpdateTask, \
    DeleteTask, UpdateProject, UserTasksCard, TaskReview, monthlyTasks

from flib.utils.sequence import AddSequence


tables = [i for i in av if i[0] in ascii_uppercase]


def getSession(req, resp, params):

    from flib.utils import helpers
    # Session.remove()
    req.session = Session()  # imported from models.db
    #print >> sys.stderr, len(req.session.dirty)
    # req.session.rollback()  ## rollback at first


def closeSession(req, resp):

    # if req.session.new or req.session.dirty:
    #req.session.commit()
    #req.session.close()
    #Session.remove()

    try:
        req.session.commit()
    except Exception, e:
        print '*' * 80
        print e
        print '*' * 80
        req.session.rollback()
    finally:
        # pass
        #req.session.rollback()
        req.session.close()
        Session.remove()


class ThingsResource:
    #@Authorize('create_collection')

    def on_get(self, req, resp, **kw):
        """Handles GET requests"""
        req.env['hooooooo'] = 'gooooooooo'
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        resp.content_type = 'text/html'
        resp.body = "pong"


class GetUserAssetTags:

    def on_get(self, req, resp, userId):
        #user = getUserInfoFromSession(req, resp)
        #resp.body = user
        resp.body = req.session.query(Tag).join(Asset.tgs).join(
            User).filter_by(id=userId).all()


class UpdateAssetTags:

    def on_post(self, req, resp, key):
        target = req.session.query(Asset).filter_by(uuid=key).first()
        data = get_params(req.stream, False)
        target.tags = data.get('tags')
        resp.status = falcon.HTTP_202


class UpdateCollectionTags:

    def on_post(self, req, resp, key):
        target = req.session.query(Collection).filter_by(uuid=key).first()
        data = get_params(req.stream, False)
        target.tags = data.get('tags')
        resp.status = falcon.HTTP_202


class UpdateProjectTags:

    def on_post(self, req, resp, key):
        target = req.session.query(Project).filter_by(uuid=key).first()
        data = get_params(req.stream, False)
        target.tags = data.get('tags')
        resp.status = falcon.HTTP_202


class DB:

    '''Restfull API for database
    '''

    #@Authorize('see_db')
    def on_get(self, req, resp, **kw):

        args = req.path.split('/')
        table = args[3]
        u = getUserInfoFromSession(req, resp)
        # if not isAuthorizedTo(u.get('id'), 'see_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        key = req.get_param('key') or 'id'
        if key:
            key = key.replace('\\', '\\\\')
        listMe = req.get_param('list')
        table = table.title()
        show = req.get_param('show')
        start = req.get_param('s')
        end = req.get_param('e')

        filters_raw = req.get_param('filters')
        add = req.get_param('add') or ''
        add = add.split(',')
        tags = req.get_param_as_list('tags') or []
        appendix = req.get_param_as_list('appendix') or []
        filters = []
        if filters_raw:
            filters += [{i.split('=')[0]:i.split('=')[1], '_':'=='}
                        for i in filters_raw.split(',') if '=' in i]
            filters += [{i.split('>')[0]:i.split('>')[1], '_':'>'}
                        for i in filters_raw.split(',') if '>' in i]
            filters += [{i.split('<')[0]:i.split('<')[1], '_':'<'}
                        for i in filters_raw.split(',') if '<' in i]

        get_count = req.get_param('count')
        sort = req.get_param('sort')
        if not sort:
            sort = 'desc'
        order_by = req.get_param('order_by')
        if not order_by:
            order_by = 'modified_on'
        try:
            if start:
                start = int(start)
            if end:
                end = int(end)
        except ValueError, e:
            print e
            start = 0
            end = 10

        if start and not end:
            end = start + 10
        if len(args) == 5:
            id = args[4]
            query = 'req.session.query({t}).filter({t}.{key}=="{id}")'.format(
                t=table, id=id, key=key)
            if get_count:
                data = eval(query).count()
                if not data:
                    resp.status = falcon.HTTP_204
                resp.body = {'count': data}
                return
            query += '.order_by({sort}({t}.{order}))'.format(sort=sort,
                                                             t=table, order=order_by)
            if start != None and end != None:
                query += '.slice(start, end)'
            data = eval(query).all()

            resp.body = data
            if not data:
                resp.status = falcon.HTTP_204

        else:
            if not show:
                query = 'req.session.query({t})'.format(t=table)
            else:
                query = 'req.session.query({t}.{f})'.format(t=table, f=show)
            try:
                if filters and isinstance(filters, list):
                    for filter in filters:
                        if isinstance(filter, dict):
                            eq = filter.pop('_')
                            query += '.filter({t}.{k}{eq}"{v}")'.format(t=table, eq=eq,
                                k=filter.keys()[0], v=filter[filter.keys()[0]])

                for tag in tags:
                    query += '.filter({t}.tgs.any(name="{tag}"))'.format(
                        t=table, tag=tag.replace('\\', '\\\\'))

                if get_count:
                    data = eval(query).count()
                    resp.body = {'count': data}
                    if not data:
                        resp.status = falcon.HTTP_204
                    return

                query += '.order_by({sort}({t}.{order}))'.format(sort=sort,
                                                                 order=order_by, t=table)

                if start != None and end != None:
                    query += '.slice(start, end)'
                data = eval(query).all()
                resp.body = data
            except (AttributeError):
                data = None
        field = req.get_param('field')
        af = req.get_param('af')  # append field
        if field:
            try:
                if len(args) != 5 and data:
                    if af:
                        data = {'message': 'not implemented'}
                    else:
                        data = [eval('i.%s' % field) for i in data]

                elif len(args) == 5:
                    '''/api/db/user/1?field=tasks'''
                    for i in data:
                        _d = getattr(i, field)
                        if isinstance(_d, list):
                            finalResult = []
                            for item in _d:
                                newDataDict = dict()
                                for key in item.__dict__.keys():
                                    value = getattr(item, key)
                                    if isinstance(value, (str, type(None), unicode, int, float, long, datetime)):
                                        newDataDict[key] = value
                                finalResult.append(newDataDict)
                            data = finalResult
                        else:
                            newDataDict = dict()
                            for key in _d.__dict__.keys():
                                value = getattr(_d, key)
                                if isinstance(value, (str, type(None), unicode, int, float, long, datetime)):
                                    newDataDict[key] = value
                            data = newDataDict

            except AttributeError, e:
                print e
                raise falcon.HTTPBadRequest(
                    'Bad Request', 'The requested field is not available for database')

            resp.body = data
            if not data:
                resp.status = falcon.HTTP_204
            return

        if len(args) == 5 and len(data) == 1 and not listMe:
            data = data[0]

            _d = {}
            #for t in add:
            #    ex = eval('data.{ad}'.format(ad=t))
            #    for i in dir(ex):
            #        if not i.startswith('_'):
            #            value = getattr(ex, i)
            #            if isinstance(value, (str, unicode, long, int, float, bool, datetime)):
            #                ex[i] = value

                #_d[t] = ex

            #print _d



            for i in dir(data):
                if not i.startswith('_'):
                    value = getattr(data, i)
                    if isinstance(value, (str, unicode, long, int, float, bool, datetime)):
                        _d[i] = value
                    # if isinstance(value, long) and i.endswith('_id'):
                    #    table = i.split('_')[0]


            resp.body = _d
            if not _d:
                resp.status = falcon.HTTP_204
        # Ok, We have an id

    def on_put(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        u = getUserInfoFromSession(req, resp)
        # if not isAuthorizedTo(u.get('id'), 'create_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        query_params = get_params(req.stream, flat=False)
        insert_cmd = '{t}(**query_params)'.format(t=table)
        new = eval(insert_cmd)
        # for i in query_params:
        #    setattr(new, i, query_params.get(i))
        resp.status = falcon.HTTP_201
        req.session.add(new)
        data = repr(new)
        resp.body = data
        # commit()

    def on_post(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        #u = getUserInfoFromSession(req)
        # if not isAuthorizedTo(u.get('id'), 'update_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        if len(args) < 5:
            resp.status = falcon.HTTP_400
            return
        id = args[4]
        # lets get the table data
        query = 'req.session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query).first()
        ##
        query_params = get_params(req.stream, flat=False)
        updated_values = []
        for key in query_params:
            if key in ['created_on', 'modified_on', 'id', 'uuid']:
                continue
            key = str(key)
            value = query_params[key]
            if isinstance(value, (int, str, unicode, float)) and hasattr(result, key):
                try:
                    setattr(result, key, value)
                    updated_values.append(key)
                except (AttributeError, TypeError):
                    continue

        # if result.update(query_params):
        resp.body = {'message': 'updated', 'info': updated_values}
        #query = 'result({q})'.format(q=query_params)
        # print eval(query)

    def on_delete(self, req, resp, **kw):
        args = req.path.split('/')
        table = args[3].title()
        #u = getUserInfoFromSession(req)
        # if not isAuthorizedTo(u.get('id'), 'delete_%s'%table):
        #    raise falcon.HTTPUnauthorized('Not Authorized', 'Permission Denied')
        if len(args) < 5:
            resp.status = falcon.HTTP_400
            return
        id = args[4]
        # lets get the table data
        query = 'req.session.query({t}).filter({t}.id=={id})'.format(
            t=table, id=int(id))
        result = eval(query).all()
        deleted = []
        for each in result:
            req.session.delete(each)
            deleted.append(each.id)
        resp.status = falcon.HTTP_202
        resp.body = {'message': 'deleted', 'info': deleted}
        #query = 'result({q})'.format(q=query_params)
        # print eval(query)


# falcon.API instances are callable WSGI apps
#app = falcon.API()
app = falcon.API(
    before=[getSession, Authenticate], after=[jsonify, closeSession])
things = ThingsResource()

########################################################
for table in tables:
    app.add_route('/api/db/{t}'.format(t=table), DB())
    app.add_route('/api/db/%s/{id}' % table, DB())
#######################################################

# things will handle all requests to the '/things' URL path
app.add_route('/api/ping', things)
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
app.add_route('/api/asset/checkout/{assetId}', AssetCheckout())
app.add_route('/api/asset/get_user_tags/{userId}', GetUserAssetTags())
app.add_route('/api/showtime/{userid}', GetUserShows())
app.add_route('/api/project', ListProjects())
app.add_route('/api/project/add', AddProject())
app.add_route('/api/project/update/{projId}', UpdateProject())
app.add_route('/api/project/get/{id}', GetProjectDetails())
app.add_route('/api/project/report/{id}/{action}', GetProjectLatestReport())
app.add_route('/api/collection/{collectionId}', CollectionInfo())
app.add_route('/api/collection/add', AddCollection())
app.add_route('/api/collection/zip/{collectionId}', ZipCollection())
app.add_route('/api/task/add/{projId}', AddTask())
app.add_route('/api/task/list/{projId}', ListTasks())
app.add_route('/api/task/{taskId}', GetTask())
app.add_route('/api/task/update/{taskId}', UpdateTask())
app.add_route('/api/task/delete/{taskId}', DeleteTask())
app.add_route('/api/task/review/{taskId}', TaskReview())
app.add_route('/api/taskcard/{date}', UserTasksCard())
app.add_route('/api/sequence/add/{projId}', AddSequence())
app.add_route('/api/sendmail', Mailer())
app.add_route('/api/report', AddReport())
app.add_route('/api/report/latest', GetUserLatestReports())
app.add_route('/api/note/get/{key}', GetNote())
app.add_route('/api/note/set/{key}', SetNote())
app.add_route('/api/note/search/{query}', SearchNote())
app.add_route('/api/user/{userId}/groups', UpdateGroups())
app.add_route('/api/user/{userId}/departements', UpdateDepartements())
app.add_route('/api/user/{userId}/expertise', UpdateExpertise())
app.add_route('/api/messages/list', GetMessagesList())
app.add_route('/api/messages/all', GetMessages())
app.add_route('/api/messages/get/{key}', GetMessage())
app.add_route('/api/messages/set', SetMessage())
app.add_route('/api/messages/search/{query}', SearchMessages())
app.add_route('/api/messages/move/{key}', MoveMessage())
app.add_route('/api/messages/delete/{key}', DeleteMessage())
app.add_route('/api/messages/update/{key}', UpdateMessage())
app.add_route('/api/setTags/asset/{key}', UpdateAssetTags())
app.add_route('/api/setTags/collection/{key}', UpdateCollectionTags())
app.add_route('/api/setTags/project/{key}', UpdateProjectTags())
app.add_route('/api/userReports', UserReports())
app.add_route('/api/monthlyTasks/{userId}', monthlyTasks())
app.add_route('/api/comment/add', AddComment())
## grid
app.add_route('/api/grid/getGridAssets/{tag}/{page}', grid.GridAssets())

app.add_route('/api/test_upload', TestUpload())


if __name__ == '__main__':
    # pass
    #import bjoern
    #bjoern.listen(app, '127.0.0.1', 5005)
    # bjoern.run()

    #from werkzeug import run_simple
    #run_simple('127.0.0.1', 5005, app, use_debugger=True, use_reloader=True)

    import tornado.httpserver
    import tornado.ioloop
    import tornado.wsgi
    container = tornado.wsgi.WSGIContainer(app)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(5005)
    tornado.ioloop.IOLoop.instance().start()

    #from gevent import wsgi
    #from gevent import monkey;monkey.patch_all()
    #wsgi.WSGIServer(('127.0.0.1', 5005), app).serve_forever()
