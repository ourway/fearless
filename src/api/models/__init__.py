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

__all__ = ['User', 'Report', 'Rule', 'Group', 'Client', 'Task',
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
r.flushdb()

from db import session, engine, Base


from models.group import Group
from models.user import User
from models.report import Report
from models.rule import Rule
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

Base.metadata.create_all(engine)

def init():
    '''set some defaults values. Like admin rule and group, managers, etc...
    '''
    print '*'*25 , 'Initializing database', '*'*25
    groups = session.query(Group.name).all()
    for gr in ['managers', 'users', 'clients', 'guests'] :
        if not gr in groups:
            new = Group(gr, rule=gr[:-1])
            session.add(new)


    rule_actions = ['can_create', 'can_read', 'can_export']
    rule_areas = ['project', 'shot', 'sequence', 'page', 'collection',
                 'report', 'scene', 'task', 'ticket']
    for act in rule_actions:
        for area in rule_areas:
            rule = '%s_%s' % (act, area)
            new = Rule(rule)
            session.add(new)




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
