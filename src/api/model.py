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
from uuid import uuid4  # for random guid generation
from utils.general import setup_logger

from sqlalchemy import create_engine  # for database
# for fields and tables
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event
# for models
from sqlalchemy_utils import PasswordType
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.exc import IntegrityError  # for exception handeling
from sqlalchemy.orm import relationship, backref  # for relationships


Base = declarative_base()
engine = create_engine('sqlite:///database/studio.db', echo=False)
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


class Rule(IDMixin, Base):

    '''Rules for permissions and authorizations
    '''

    name = Column(String(32))
    groups = relationship("Group",
                          secondary=groups_rules, backref='rules')


class Group(Base):

    '''Groups for membership management
    '''
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    users = relationship('User', backref='group')


class User(Base):

    '''Main users group
    '''
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String(32), unique=True)
    email = Column(String(64), unique=True)
    password = Column( PasswordType(schemes=['pbkdf2_sha512']) )
    token = Column(String(64), default=getUUID, unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.datetime.utcnow)
    firstname = Column(String(64), nullable=True)
    lastname = Column(String(64), nullable=True)
    age = Column(Integer)
    group_id = Column(Integer, ForeignKey('group.id'))
    reports = relationship('Report', backref='user')
    # group =
    #reports = Set("Report")
    #groups = Set("Group")

    def __repr__(self):
        return "<User(login='%s', email='%s', id='%s')>" % (
            self.login, self.email, self.id)


class Report(Base):

    '''All reports will be saved here
    '''
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    body = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey("project.id"))


class Project(Base):

    '''Studio Projects
    '''
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    name = Column(String(64), unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
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


class Client(Base):

    '''The Client (e.g. a company) which users may be part of.
    '''
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    users = relationship('User', backref='company', secondary='client_users')


class Repository(Base):

    """Manages fileserver/repository related data.
    """
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    linux_path = Column(String(256))
    windows_path = Column(String(256))
    osx_path = Column(String(256))
    ftp_path = Column(String(256))
    sftp_path = Column(String(256))
    webdav_path = Column(String(256))


class Task(Base):

    """Task management
    """
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
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


class Ticket(Base):

    """Tickets are the way of reporting errors or asking for changes.
    """
    __tablename__ = 'ticket'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    project_id = Column(Integer, ForeignKey("project.id"))
    name = Column(String(64), unique=True)
    body = Column(Text)


class Version(Base):

    """Holds information about the created versions (files) for a class:`.Task`
    """
    __tablename__ = 'version'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    take_name = Column(String(256))
    version_number = Column(Integer)
    is_published = Column(Boolean, default=False)


class Tag(Base):

    """Used for any tag in orm
    """
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)


class Page(Base):

    """Implements o simple page structure for wikis
    """
    __tablename__ = 'page'

    id = Column(Integer, primary_key=True)
    title = Column(String(256), unique=True)
    content = Column(Text)


class Shot(Base):

    """Shot data
    """
    __tablename__ = 'shot'

    id = Column(Integer, primary_key=True)
    sequences = relationship(
        'Sequence', secondary='shot_sequence', backref='shots')
    scenes = relationship('Scene', secondary='shot_scene', backref='shots')
    cut_in = Column(Integer, default=1)
    cut_out = Column(Integer)


class Sequence(Base):

    """Sequence data
    """
    __tablename__ = 'sequence'

    id = Column(Integer, primary_key=True)


class Scene(Base):

    """Scene data
    """
    __tablename__ = 'scene'

    id = Column(Integer, primary_key=True)


############# Events ################

def logUserCreation(mapper, connection, target):
    logger.info('New user added|{t.id}|{t.login}'.format(t=target))

event.listen(User, 'after_insert', logUserCreation)

#####################################
#####################################
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
#####################################
#####################################


if __name__ == '__main__':
    ed_user = User(login='ed', firstname='Ed Jones', password='edspassword',
                   email='farsheed.ashouri@gmail.com')
    session.add(ed_user)
    try:
        session.commit()
    except IntegrityError:
        print 'User "%s" information is not unique' % ed_user.login
        session.rollback()

    user = session.query(User).first()
    for report in session.query(Report).all():
        print report.body
