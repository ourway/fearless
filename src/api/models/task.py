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
from ftfy import fix_text
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event, Unicode

import json as json
from mako.template import Template
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, convert_to_datetime, now
from sqlalchemy.orm.collections import attribute_mapped_collection
from utils.helpers import tag_maker, account_maker

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


tasks_accounts = Table("tasks_accounts", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "task_id", Integer, ForeignKey("task.id"), primary_key=True),
                     Column(
                         "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                     )

tasks_tags = Table("tasks_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "task_id", Integer, ForeignKey("task.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


task_relations = Table(
    'task_relations', Base.metadata,
    Column('task_a_id', Integer, ForeignKey('task.id')),
    Column('task_b_id', Integer, ForeignKey('task.id')))


class Task(IDMixin, Base):

    """Task management
    """
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    title = Column(Unicode(128), nullable=False)
    note = Column(String(512))  # task note
    description = Column(String(512))  # task note
    gauge = Column(String(64))  # task note
    start = Column(DateTime, nullable=False, default=now)
    computed_start = Column(DateTime)
    computed_end = Column(DateTime)
    end = Column(DateTime, nullable=False)
    duration = Column(Float(precision=3), default=0)
    period = relationship("Date", uselist=False)
    effort = Column(Float(precision=3), nullable=False, default=0)
    effort_left = Column(Float(precision=3), default=0)
    effort_done = Column(Float(precision=3), default=0)
    length = Column(Float(precision=3), default=0)
    criticalness = Column(Float(precision=3), default=0)
    onstart_charge = Column(Float(precision=3), default=0)
    active = Column(Boolean, default=True)
    onend_charge = Column(Float(precision=3), default=0)
    milestone = Column(Boolean, default=False)  # is task a milestone?
    parent_id = Column(Integer, ForeignKey("task.id"))
    parent = relationship(
        'Task', backref='children', remote_side=[id], uselist=True)
    reports = relationship('Report', backref='task')
    resources = relationship('User', backref='tasks', secondary='task_users')
    alternative_resources = relationship(
        'User', backref='alternative_for', secondary='task_alternative')
    watchers = relationship(
        'User', backref='watches_tasks', secondary='task_watchers')
    responsibles = relationship(
        'User', backref='responsible_of', secondary='task_responsible')
    priority = Column(Integer, default=500)
    complete = Column(Integer, default=0)
    computed_complete = Column(Integer, default=0)
    version = relationship('Version', backref='task')
    #task = relationship('Task', backref='parent')
    ######### GOLDEN SOLUSION : Nested tree  for task to task relations ######

    depends = relationship("Task", secondary=task_relations,
                           primaryjoin=id == task_relations.c.task_a_id,
                           secondaryjoin=id == task_relations.c.task_b_id,
                           backref='dependent_of')
    acns = relationship("Account", backref='tasks', secondary="tasks_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='tasks', secondary="tasks_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)


    ##########################################################################

    # def __repr__(self):
    #    return self.title

    #@property
    def tjp_task(self):
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/task.tji')
        t = Template(filename=templateFile)
        subtask = '\n'.join([i.tjp_task() for i in self.children])
        return t.render(task=self, subtask=subtask)

    def dump(self, _indent=0):
        return repr(self)

    @validates('title')
    def check_name(self, key, data):
        # print key, task
        return fix_text(data)

    @validates('responsibles')
    def update_resources(self, key, data):
        # if not data in self.resources:
        #    self.resources.append(data)
        return data

    @property
    def go(self):
        return 5

    @validates('start')
    def _check_start(self, key, data):
        if data == 'now':
            data = datetime.datetime.utcnow()
        else:
            data = convert_to_datetime(data)

        if data and self.project and self.project.end:
            try:
                data = min(data, self.project.end)
            except TypeError:
                pass

        if self.project:
            if data == self.project.end and self.effort:
                # approximate fix
                data = data - datetime.timedelta(hours=self.effort * 4)

        if isinstance(data, datetime.datetime):
            return data
        else:
            return now()

    @validates('end')
    def _check_end(self, key, data):
        end = convert_to_datetime(data)
        start = convert_to_datetime(self.start)
        if start and end:
            data = max(start, end)  # if any errors in end
        if data and self.project and self.project.end:
            try:
                data = min(data, self.project.end)
            except TypeError:
                pass

        #delta = data - start
        self.end_set = True
        # if not hasattr(self, 'effort_set'):
        #    self.duration = delta.days * 24 + delta.seconds / 3600.0
        if isinstance(data, datetime.datetime):
            return data
        else:
            return now()

    @validates('computed_start')
    def _update_computed_start(self, key, data):
        return convert_to_datetime(data)

    @validates('computed_end')
    def _update_computed_end(self, key, data):
        return convert_to_datetime(data)

    @validates('effort')
    def _update_end(self, key, data):
        if data:
            data = float(data)
        if not self.start:
            self.start = now()
        delta = datetime.timedelta(hours=data)
        self.effort_set = True
        if not hasattr(self, 'end_set'):
            self.end = self.start + delta
        return data

    @validates('complete')
    def _check_complete(self, key, data):
        if data:
            data = int(float(data))
        return data



