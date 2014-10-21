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
    lastname = Column(String(64), nullable=True)
    lastLogIn = Column(DateTime)
    age = Column(Integer)
    active = Column(Boolean, default=False)
    reports = relationship('Report', backref='user')

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

event.listen(User, 'before_insert', logUserCreation)
