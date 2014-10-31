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

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property

from mixin import IDMixin, Base, getUUID, logger
import datetime





class User(IDMixin, Base):

    '''Main users group
    '''
    email = Column(String(64), unique=True, nullable=False)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    token = Column(String(64), default=getUUID, unique=True)
    firstname = Column(String(64), nullable=True)
    alias = Column(String(64), nullable=True)
    lastname = Column(String(64), nullable=True)
    lastLogIn = Column(DateTime)
    age = Column(Integer)
    daily_working_hours = Column(Integer, default=8)
    off_days = Column(String(32), default='fri')
    active = Column(Boolean, default=False)
    rate = Column(Float(precision=5), default = 1.850)
    reports = relationship('Report', backref='user')


    @validates('email')
    def _validate_email(self, key, data):
        if re.match(r'[^@]+@[^@]+\.[^@]+', data):
            if not self.alias:
                self.alias = data.split('@')[0].replace('.', '_')
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
