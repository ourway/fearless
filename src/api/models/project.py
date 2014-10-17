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


from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event, func

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base

project_users = Table('project_users', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('project_id', Integer, ForeignKey('project.id')),
                     Column('user_id', Integer, ForeignKey('user.id'))
                     )


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
