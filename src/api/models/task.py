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

import os
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

import ujson as json
from db import session
from mako.template import Template
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, convert_to_datetime, now, BaseNestedSets
from sqlalchemy.orm.collections import attribute_mapped_collection

task_users = Table('task_users', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )

task_watchers = Table('task_watchers', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )

task_responsible = Table('task_responsible', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )

task_alternative = Table('task_alternative', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )



task_relations = Table(
    'task_relations', Base.metadata,
    Column('task_a_id', Integer, ForeignKey('task.id')),
    Column('task_b_id', Integer, ForeignKey('task.id')))


class Task(IDMixin, Base, BaseNestedSets):

    """Task management
    """
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    title = Column(String(64), nullable=False)
    note = Column(String(256))  ## task note
    start = Column(DateTime, nullable=False, default=now)
    end = Column(DateTime, nullable=False)
    duration = Column(Float(precision=3), default=0)
    effort = Column(Float(precision=3), nullable=False, default=1)
    length = Column(Float(precision=3), default=0)
    milestone = Column(Boolean, default=False) # is task a milestone?
    parent_id = Column(Integer, ForeignKey("task.id"))

    resources = relationship('User', backref='tasks', secondary='task_users')
    alternative_resources = relationship(
        'User', backref='alternative_for', secondary='task_alternative')
    watchers = relationship(
        'User', backref='watches', secondary='task_watchers')
    responsibles = relationship(
        'User', backref='responsible_of', secondary='task_responsible')
    priority = Column(Integer, default=500)
    complete = Column(Integer, default=0)
    version = relationship('Version', backref='task')
    #task = relationship('Task', backref='parent')
    ######### GOLDEN SOLUSION : Nested tree  for task to task relations ######

    depends = relationship("Task", secondary=task_relations,
                           primaryjoin=id == task_relations.c.task_a_id,
                           secondaryjoin=id == task_relations.c.task_b_id,
                           backref='dependent_of')
    ##########################################################################

    #def __repr__(self):
    #    return self.title

    #@property
    def tjp_task(self):
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/task.tjp')
        t = Template(filename=templateFile)
        subtask = '\n'.join([i.tjp_task() for i in self.children])
        return t.render(task=self, subtask=subtask)

    def dump(self, _indent=0):
        return repr(self)

    @validates('name')
    def check_name(self, key, task):
        # print key, task
        return task

    @validates('responsibles')
    def update_resources(self, key, data):
        if not data in self.resources:
            self.resources.append(data)
        return data


    @property
    def go(self):
        return 5

    @validates('start')
    def _check_start(self, key, data):
        if data == 'now':
            data = datetime.datetime.utcnow()
        else:
            data =  convert_to_datetime(data)
        if self.project and self.project.end:
            data = min(data, self.project.end)

        if self.project:
            if data == self.project.end and self.effort:
                data = data - datetime.timedelta(hours=self.effort*4) ## approximate fix
        return data



    @validates('end')
    def _check_end(self, key, data):
        end = convert_to_datetime(data)
        start = convert_to_datetime(self.start)
        data = max(start, end)  ## if any errors in end
        if self.project and self.project.end:
            data = min(data, self.project.end)



        delta = data - start
        self.end_set = True
        #if not hasattr(self, 'effort_set'):
        #    self.duration = delta.days * 24 + delta.seconds / 3600.0
        return data



    @validates('effort')
    def _update_end(self, key, data):
        if not self.start:
            self.start = now()
        delta = datetime.timedelta(hours=data)
        self.effort_set = True
        if not hasattr(self, 'end_set'):
            self.end = self.start + delta
        return data



@event.listens_for(Task, 'before_insert')
def receive_before_insert(mapper, connection, target):
    target.effort = target.effort or 0

    # ... (event handling logic) ...


@event.listens_for(Task, 'after_insert')
def receive_before_insert(mapper, connection, target):
    pass
    #print target.title
    # ... (update task confighandling logic) ...


#def schedule(mapper, connection, target):

    #target.project.plan()


#event.listen(Task, 'after_insert', schedule)
