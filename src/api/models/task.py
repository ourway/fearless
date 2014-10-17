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
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base


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

