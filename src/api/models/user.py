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

import re
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event
from . import session, Group
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base, getUUID, logger
import datetime

users_groups = Table('users_groups', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )
class User(IDMixin, Base):

    '''Main users group
    '''
    email = Column(String(64), unique=True, nullable=False)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    token = Column(String(64), default=getUUID, unique=True)
    firstname = Column(String(64), nullable=True)
    alias = Column(String(64), nullable=True, unique=True)
    lastname = Column(String(64), nullable=True)
    lastLogIn = Column(DateTime)
    age = Column(Integer)
    efficiency = Column(Float(precision=3), default=0.75)
    daily_working_hours = Column(Integer, default=8)
    off_days = Column(String(32), default='fri')
    latest_session_id = Column(String(64))
    active = Column(Boolean, default=False)
    rate = Column(Float(precision=5), default=1.850)
    reports = relationship('Report', backref='user')
    grps = relationship('Group', backref='users', secondary='users_groups')
    groups = association_proxy('grps', 'name')

    @validates('email')
    def _validate_email(self, key, data):
        if re.match(r'[^@]+@[^@]+\.[^@]+', data):
            if not self.alias:
                self.alias = data.split('@')[0].replace('.', '_')

            self.groups.append(self.alias)

            return data

    @validates('id')
    def authorize_first_user(self, key, data):
        return data

    @hybrid_property
    def fullname(self):
        return (self.firstname or '<>') + " " + (self.lastname or '<>')
    # group =
    #reports = Set("Report")
    #groups = Set("Group")


def logUserCreation(mapper, connection, target):
    logger.info('New user added|{t.id}|{t.email}'.format(t=target))
    #new_group = Group(name=target.login)
    #target.group= new_group
    # session.add(new_group)

event.listen(User, 'after_insert', logUserCreation)
