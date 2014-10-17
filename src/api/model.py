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

__all__ = ['User', 'Report', 'Rule', 'Group', 'Client', 'Task', 'Repository', 'Project',
           'Ticket', 'session', 'IntegrityError']

import datetime
import ujson as json
from uuid import uuid4  # for random guid generation
from utils.general import setup_logger

from sqlalchemy import create_engine, func  # for database
# for fields and tables
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event
# for models
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.exc import IntegrityError  # for exception handeling
from sqlalchemy.orm import relationship, backref  # for relationships


Base = declarative_base()
db_path = 'database/studio.db'
#db_path = ':memory:'
engine = create_engine('sqlite:///%s'%db_path, echo=False)
logger = setup_logger('model', 'model.log')


def getUUID():
    return str(uuid4())


groups_rules = Table('group_rules', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('rule_id', Integer, ForeignKey('rule.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )

project_users = Table('project_users', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('user_id', Integer, ForeignKey('user.id'))
                      )

client_users = Table('client_users', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('client_id', Integer, ForeignKey('client.id')),
                     Column('user_id', Integer, ForeignKey('user.id'))
                     )

task_users = Table('task_users', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )

task_watchers = Table("task_watchers", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "task_id", Integer, ForeignKey("task.id"), primary_key=True),
                      Column(
                          "watcher_id", Integer, ForeignKey("user.id"), primary_key=True)
                      )


task_responsible = Table("task_responsible", Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column(
                             "task_id", Integer, ForeignKey("task.id"), primary_key=True),
                         Column(
                             "responsible_id", Integer, ForeignKey("user.id"), primary_key=True)
                         )

shot_sequence = Table("shot_sequence", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                      Column("sequence_id", Integer, ForeignKey(
                          "sequence.id"), primary_key=True)
                      )

shot_scene = Table("shot_scene", Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column(
                       "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                   Column(
                       "scene_id", Integer, ForeignKey("scene.id"), primary_key=True)
                   )


class IDMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #__table_args__ = {'mysql_engine': 'InnoDB'}
    #__mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    @property
    def columns(self):
        return [ c.name for c in self.__table__.columns ]

    @property
    def columnitems(self):
        return dict([ (c, getattr(self, c)) for c in self.columns ])

    def __repr__(self):
        return json.dumps('{}({})'.format(self.__class__.__name__, self.columnitems))



class Rule(IDMixin, Base):

    '''Rules for permissions and authorizations
    '''

    name = Column(String(32))
    groups = relationship("Group",
                          secondary=groups_rules, backref='rules')


class Group(IDMixin, Base):

    '''Groups for membership management
    '''
    name = Column(String(32))
    users = relationship('User', backref='group')


class User(IDMixin, Base):

    '''Main users group
    '''

    login = Column(String(32), unique=True)
    email = Column(String(64), unique=True)
    password = Column( PasswordType(schemes=['pbkdf2_sha512']) )
    token = Column(String(64), default=getUUID, unique=True)

    firstname = Column(String(64), nullable=True)
    lastname = Column(String(64), nullable=True)

    age = Column(Integer)
    group_id = Column(Integer, ForeignKey('group.id'))
    reports = relationship('Report', backref='user')


    @hybrid_property
    def fullname(self):
        return (self.firstname or '<>') + " " + (self.lastname or '<>')
    # group =
    #reports = Set("Report")
    #groups = Set("Group")



class Report(IDMixin, Base):

    '''All reports will be saved here
    '''
    body = deferred(Column(Text)) ## load on access
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey("project.id"))


class Project(IDMixin, Base):

    '''Studio Projects
    '''
    active = Column(Boolean, default=True)
    name = Column(String(64), unique=True)
    client_id = Column(Integer, ForeignKey("client.id"))
    client = relationship('Client', backref='projects')
    tasks = relationship(
        'Task', backref='project', cascade="all, delete-orphan")
    users = relationship('User', backref='projects', secondary='project_users')
    lead_id = Column(Integer, ForeignKey("user.id"))
    lead = relationship('User', backref='projects_lead')
    director = relationship('User', backref='directs')
    repository_id = Column(Integer, ForeignKey("repository.id"))
    repository = relationship('Repository', backref='projects')
    is_stereoscopic = Column(Boolean, default=False)
    fps = Column(Float(precision=3), default=False)
    tickets = relationship('Ticket', backref='project')
    reports = relationship('Report', backref='project')
    @aggregated('tasks', Column(Integer))
    def calculate_number_of_tasks(self):
        return func.sum('1') 



class Client(IDMixin, Base):

    '''The Client (e.g. a company) which users may be part of.
    '''
    name = Column(String(64), unique=True)
    users = relationship('User', backref='company', secondary='client_users')


class Repository(IDMixin, Base):

    """Manages fileserver/repository related data.
    """
    linux_path = Column(String(256))
    windows_path = Column(String(256))
    osx_path = Column(String(256))
    ftp_path = Column(String(256))
    sftp_path = Column(String(256))
    webdav_path = Column(String(256))


class Task(IDMixin, Base):

    """Task management
    """
    id = Column(Integer, primary_key=True)  ## over-ride mixin version. because of remote_side
    project_id = Column(Integer, ForeignKey("project.id"))
    name = Column(String(64), unique=True)
    parent_id = Column(Integer, ForeignKey("task.id"))
    children = relationship(
        'Task', backref=backref('parent', remote_side=[id]))
    resources = relationship('User', backref='tasks', secondary='task_users')
    watchers = relationship(
        'User', backref='watches', secondary='task_watchers')
    responsibles = relationship(
        'User', backref='responsible_of', secondary='task_responsible')
    priority = Column(Integer)

    @validates('name')
    def check_name(self, key, task):
        # print key, task
        return task

    @property
    def go(self):
        return 5


class Ticket(IDMixin, Base):

    """Tickets are the way of reporting errors or asking for changes.
    """
    project_id = Column(Integer, ForeignKey("project.id"))
    name = Column(String(64), unique=True)
    body = deferred(Column(Text))


class Version(IDMixin, Base):

    """Holds information about the created versions (files) for a class:`.Task`
    """
    take_name = Column(String(256))
    version_number = Column(Integer)
    is_published = Column(Boolean, default=False)


class Tag(IDMixin, Base):

    """Used for any tag in orm
    """
    name = Column(String(64), unique=True)


class Page(IDMixin, Base):

    """Implements o simple page structure for wikis
    """
    title = Column(String(256), unique=True)
    content = Column(Text)


class Shot(IDMixin, Base):

    """Shot data
    """
    sequences = relationship(
        'Sequence', secondary='shot_sequence', backref='shots')
    scenes = relationship('Scene', secondary='shot_scene', backref='shots')
    cut_in = Column(Integer, default=1)
    cut_out = Column(Integer)


class Sequence(IDMixin, Base):

    """Sequence data
    """



class Scene(IDMixin, Base):

    """Scene data
    """


#####################################
#####################################
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
#####################################
#####################################
############# Events ################

def logUserCreation(mapper, connection, target):
    logger.info('New user added|{t.id}|{t.login}'.format(t=target))
    #new_group = Group(name=target.login)
    #target.group= new_group
    #session.add(new_group)

event.listen(User, 'before_insert', logUserCreation)




if __name__ == '__main__':

    #import os
    #os.remove('database/studio.db')

    #ed_user = User(login='ed', firstname='Ed Jones', password='edspassword',
    #               email='farsheed.ashouri@gmail.com')


    

    #session.add_all([ed_user])
    #session.commit()
    ed_user = session.query(User).first()
    if not ed_user:
        ed_user = User(login='ed', firstname='Ed Jones', password='edspassword',
                   email='farsheed.ashouri@gmail.com')

    session.add(ed_user)
    session.commit()
    print ed_user.created_on

    ed_user.lastname = 'Ashouri'
    print ed_user.modified_on
    #print session.query(Group).all()
    #project1 = Project(name="my new project")
    #task1 = Task(name='animate', project=project1)




