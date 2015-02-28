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
           'Repository', 'Project', 'now', 'Ticket',
           'Version', 'Tag', 'Shot', 'Asset', 'Scene', 'Sequence',
           'Document', 'Account', 'Date', 'Collection', 'r', 'Departement',
           'Comment', 'fdb', 'vdb', 'adb', 'rdb', 'ddb', 'mdb', 'riakClient', 'Expert']

import os

# for models
from flib.models.mixin import now
from sqlalchemy.exc import IntegrityError  # for exception handeling
from sqlalchemy.sql import between
import redis
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
# r.flushdb()

from flib.models.db import session_factory, engine, Base
session = session_factory()


from flib.models.group import Group
from flib.models.document import Document
from flib.models.account import Account
from flib.models.report import Report
from flib.models.role import Role
from flib.models.client import Client
from flib.models.project import Project
from flib.models.repository import Repository
from flib.models.task import Task
from flib.models.ticket import Ticket
from flib.models.shot import Shot
from flib.models.sequence import Sequence
from flib.models.scene import Scene
from flib.models.tag import Tag
from flib.models.version import Version
from flib.models.asset import Asset
from flib.models.collection import Collection
from flib.models.departement import Departement
from flib.models.document import Document
from flib.models.comment import Comment
from flib.models.date import Date
from flib.models.expert import Expert
from flib.models.user import User
from flib.utils.defaults import public_repository_path
Base.metadata.create_all(engine)


def init():
    '''set some defaults values. Like admin role and group, managers, etc...
    '''
    groups = session.query(Group).all()
    deps = session.query(Departement).all()
    exps = session.query(Expert).all()
    departements = ['animation', 'rigging', 'character', 'storyboard', 'voice', 'sound', 'texture', 'layout', 'editorial', 'technical',
                    'story', 'rendering', 'compositing', 'lighting', 'dynamics', 'stereoscopic', 'staff', 'management', 'directing', 'art']

    experts = ['character design', 'character concept', 'matte paint', 'composite', 'mel scripting', 'python programming', 'team management',
               'directing', 'hair dynamic', 'hair style', 'cloth dynamic', 'cloth design', 'arnold technical', 'renderman technical', 'nuke', 'maya',
               'adobe photoshop', 'zbrush', 'mudbox', 'toxik', 'fluid', 'character modeling', 'set modeling', 'set designer', 'set concept',
               'technical directing', 'office tools', 'concept painter', 'character shading', 'character paint', '2d motion design',
               'motion bulder', 'motion capture', 'sound design', 'editing', 'adobe premiere', 'uv layout', 'ptex', 'character animation',
               'rigging', 'skinning', 'blend shape', 'prop design', 'prop concept', 'storyboard', 'screenplay', 'story', 'planning', 'texturing',
               '2d layout', '3d layout', 'animatic', 'previz', 'camera', 'cinematography', 'lighting', 'tracking', 'dispatching', 'rendering rnd',
               'software developer', 'it', 'dba', 'finance', 'supervisor', 'character cloth concept', 'character cloth design']

    for exp in experts:
        if not exp in [i.name for i in exps]:
            new = Expert(name=exp)
            session.add(new)

    for dep in departements:
        if not dep in [i.name for i in deps]:
            new = Departement(name=dep)
            session.add(new)

    for gr in ['managers', 'users', 'clients', 'guests', 'admin']:
        if not gr in [i.name for i in groups]:
            new = Group(gr, role=gr[:-1], typ='general')
            if gr in departements:
                new.typ = 'departement'
            session.add(new)

    manager_group = session.query(Group).filter(
        Group.name == 'managers').first()
    admin_group = session.query(Group).filter(Group.name == 'admin').first()
    user_group = session.query(Group).filter(Group.name == 'users').first()

    role_actions = ['create', 'see', 'delete', 'edit']
    role_areas_managers = ['project', 'collection', 'repository', 'database']
    role_areas_users = ['tag', 'asset', 'ticket', 'shot',
                        'sequence', 'report', 'scene', 'document', 'task', 'user']
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
    users_group = session.query(Group).filter(Group.name == 'users').first()
    for role in read_roles:
        users_group.rls.append(role)

    for repo in ['profiles', 'reports', 'assets', 'showtime']:
        new_repository = session.query(Repository).filter(
            Repository.name == repo).first()
        if not new_repository:
            new_repository = Repository(
                name=repo, path=os.path.join(public_repository_path, repo))
            session.add(new_repository)

    session.commit()
    session.close()


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
