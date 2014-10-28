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

import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, convert_to_datetime
from sqlalchemy.orm.collections import attribute_mapped_collection

task_users = Table('task_users', Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column('task_id', Integer, ForeignKey('task.id')),
                   Column('user_id', Integer, ForeignKey('user.id'))
                   )



task_alt_users = Table('task_alt_users', Base.metadata,
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
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    project_id = Column(Integer, ForeignKey("project.id"))
    title = Column(String(64), unique=True, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    duration = Column(Float(precision=3), nullable=False)
    parent_id = Column(Integer, ForeignKey("task.id"))


    depends = association_proxy(
        'task_depends_on',
        'depends_on',
        creator=lambda n: TaskDependency(depends_on=n)
    )

    dependent = association_proxy(
        'task_dependent_of',
        'dependent_of',
        creator=lambda n: TaskDependency(dependent_of=n)
    )

    resources = relationship('User', backref='tasks', secondary='task_users')
    alternative_resources = relationship('User', backref='alternative_for', secondary='task_alt_users')
    watchers = relationship(
        'User', backref='watches', secondary='task_watchers')
    responsibles = relationship(
        'User', backref='responsible_of', secondary='task_responsible')
    priority = Column(Integer, default=5)
    version = relationship('Version', backref='task')
    #task = relationship('Task', backref='parent')

    def __repr__(self):
        return "Task(title=%r, id=%r, parent_id=%r)" % (
                    self.title,
                    self.id,
                    self.parent_id
                )

    def dump(self, _indent=0):
        return repr(self)

    @validates('name')
    def check_name(self, key, task):
        # print key, task
        return task

    @property
    def go(self):
        return 5

    @validates('start')
    def _check_start(self, key, data):
        if data == 'now':
            return datetime.datetime.utcnow()
        return convert_to_datetime(data)


    @validates('end')
    def _check_end(self, key, data):
        end = convert_to_datetime(data)
        start = convert_to_datetime(self.start)
        delta = end-start
        self.end_set = True
        if not hasattr(self, 'duration_set'):
            self. duration = delta.days*24 + delta.seconds / 3600.0

        return end

    @validates('duration')
    def _update_end(self, key, data):
        delta = datetime.timedelta(hours=data)
        self.duration_set = True
        if not hasattr(self, 'end_set'):
            self.end = self.start + delta
        return data

    @validates('depends_on')
    def _add_other_dependencies(self, key, data):
        return data

    @validates('dependent_of')
    def _add_other_dependents_of(self, key, data):
        return data





class TaskDependency(IDMixin, Base):

    depends_on_id = Column(Integer,
                        ForeignKey('task.id'),
                        )

    dependent_of_id = Column(Integer,
                        ForeignKey('task.id'),
                        )

    depends_on = relationship('Task',
                                primaryjoin=depends_on_id==Task.id,
                                backref='task_depends_on')
    dependent_of = relationship('Task',
                                primaryjoin=dependent_of_id==Task.id,
                                backref='task_dependent_of')






def schedule(mapper, connection, target):
    pass
    #print target


event.listen(Task, 'after_insert', schedule)

