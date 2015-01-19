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


'''
usage:

    from model import *
    print session.query(Report).all()
'''

__all__ = ['User', 'Report', 'Role', 'Group', 'Client', 'Task',
           'Repository', 'Project', 'now', 'Ticket', 'session',
           'Version', 'Tag', 'Shot', 'Asset', 'Scene', 'Sequence',
           'Document', 'Account', 'Date' ,'Collection', 'r', 'es', 'Departement',
           'Comment', 'fdb', 'vdb', 'adb', 'rdb', 'ddb', 'mdb', 'riakClient']

import os

# for models
from mixin import now
from sqlalchemy.exc import IntegrityError  # for exception handeling
from sqlalchemy.sql import between
import redis

from elasticsearch import Elasticsearch
es = Elasticsearch()

# db number 1 and 2 are for celery
r = redis.StrictRedis(host='localhost', port=6379, db=3)

import riak
riakClient = riak.RiakClient(pb_port=8087)
fdb = riakClient.bucket('fearless_file_database')
vdb = riakClient.bucket('fearless_video_database')
adb = riakClient.bucket('fearless_asset_database')
rdb = riakClient.bucket('fearless_reports_database')

ddb = riakClient.bucket('fearless_documents_database')
riakClient.create_search_index('fearless_documents_database')
ddb.set_properties({'search_index': 'fearless_documents_database'})
ddb.enable_search()

mdb = riakClient.bucket('fearless_messages_database')
riakClient.create_search_index('fearless_messages_database')
mdb.set_properties({'search_index': 'fearless_messages_database'})
mdb.enable_search()
#r.flushdb()

from db import session, engine, Base


from models.group import Group
from models.document import Document
from models.account import Account
from models.user import User
from models.report import Report
from models.role import Role
from models.client import Client
from models.project import Project
from models.repository import Repository
from models.task import Task
from models.ticket import Ticket
from models.shot import Shot
from models.sequence import Sequence
from models.scene import Scene
from models.tag import Tag
from models.version import Version
from models.asset import Asset
from models.collection import Collection
from models.departement import Departement
from models.document import Document
from models.comment import Comment
from models.date import Date
from utils.defaults import public_repository_path
Base.metadata.create_all(engine)

def init():
    '''set some defaults values. Like admin role and group, managers, etc...
    '''
    groups = session.query(Group).all()
    departements = ['animation', 'rigging', 'character', 'storyboard', 'voice', 'sound', 'texture', 'layout', 'editorial', 'technical',
                    'story', 'rendering', 'compositing', 'lighting', 'dynamics', 'stereoscopic', 'staff', 'management', 'directing', 'art']

    for gr in ['managers', 'users', 'clients', 'guests', 'admin']:
        if not gr in [i.name for i in groups]:
            new = Group(gr, role=gr[:-1], typ='general')
            if gr in departements:
                new.typ = 'departement'
            session.add(new)

    manager_group = session.query(Group).filter(Group.name=='managers').first()
    admin_group = session.query(Group).filter(Group.name=='admin').first()
    user_group = session.query(Group).filter(Group.name=='users').first()

    role_actions = ['create', 'see', 'delete', 'edit']
    role_areas_managers = ['project', 'collection', 'repository', 'database']
    role_areas_users = ['tag', 'asset', 'ticket', 'shot', 'sequence', 'report', 'scene', 'document', 'task', 'user']
    roles = session.query(Role).all()
    for act in role_actions:
        for area in role_areas_managers + role_areas_users:
            role = '%s_%s' % (act, area)
            if not role in [i.name for i in roles]:
                new = Role(role)
                session.add(new)
                if area in role_areas_users:
                    user_group.rls.append(new)
                manager_group.rls.append(new)
                admin_group.rls.append(new)

    read_roles = session.query(Role).filter(Role.name.like('see%')).all()
    users_group = session.query(Group).filter(Group.name=='users').first()
    for role in read_roles:
        users_group.rls.append(role)

    for repo in ['profiles', 'reports', 'assets', 'showtime']:
        new_repository = session.query(Repository).filter(Repository.name == repo).first()
        if not new_repository:
            new_repository = Repository(name=repo, path= os.path.join(public_repository_path, repo))
            session.add(new_repository)

    session.commit()


init()




if __name__ == '__main__':

    #import os
    # os.remove('database/studio.db')

    # ed_user = User(login='ed', firstname='Ed Jones', password='edspassword',
    #               email='farsheed.ashouri@gmail.com')

    # session.add_all([ed_user])
    # session.commit()

    ed_user = User(login='ed', firstname='Ed Jones', password='edspassword',
                   email='farsheed.ashouri@gmail.com')

    session.add(ed_user)
    session.commit()
    print ed_user.created_on

    ed_user.lastname = 'Ashouri'
    print ed_user.modified_on
    # print session.query(Group).all()
    #project1 = Project(name="my new project")
    #task1 = Task(name='animate', project=project1)
