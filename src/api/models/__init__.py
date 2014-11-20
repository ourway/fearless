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
           'Page', 'Collection', 'r', 'es', 'Departement']

import os

# for models
from mixin import now
from sqlalchemy.exc import IntegrityError  # for exception handeling
import redis

from elasticsearch import Elasticsearch
es = Elasticsearch()

# db number 1 and 2 are for celery
r = redis.StrictRedis(host='localhost', port=6379, db=3)
#r.flushdb()

from db import session, engine, Base


from models.group import Group
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
from models.page import Page
from models.asset import Asset
from models.collection import Collection
from models.departement import Departement
from utils.defaults import public_repository_path
Base.metadata.create_all(engine)

def init():
    '''set some defaults values. Like admin role and group, managers, etc...
    '''
    print '*'*25 , 'Initializing database', '*'*25
    groups = session.query(Group).all()
    for gr in ['managers', 'users', 'clients', 'guests'] :
        if not gr in [i.name for i in groups]:
            new = Group(gr, role=gr[:-1])
            session.add(new)

    manager_group = session.query(Group).filter(Group.name=='managers').first()
    user_group = session.query(Group).filter(Group.name=='users').first()

    role_actions = ['create', 'see', 'delete', 'edit']
    role_areas_managers = ['project', 'collection', 'repository', 'database']
    role_areas_users = ['tag', 'asset', 'ticket', 'shot', 'sequence', 'report', 'scene', 'page', 'task', 'user']
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

    read_roles = session.query(Role).filter(Role.name.like('see%')).all()
    users_group = session.query(Group).filter(Group.name=='users').first()
    for role in read_roles:
        print role
        users_group.rls.append(role)

    profile_files_repository = session.query(Repository).filter(Repository.name == 'profiles').first()
    if not profile_files_repository:
        profile_files_repository = Repository(name='profiles', path= os.path.join(public_repository_path, 'profiles'))
        session.add(profile_files_repository)

    session.commit()
    print '*'*25 , '*********************', '*'*25


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
