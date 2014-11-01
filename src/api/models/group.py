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


users_groups = Table('users_groups', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )


class Group(IDMixin, Base):

    '''Groups for membership management
    '''
    name = Column(String(32), nullable=False, unique=True)
    users = relationship('User', backref='groups', secondary='users_groups')
