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
from mixin import IDMixin, Base, getUUID



groups_rules = Table('group_rules', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('rule_id', Integer, ForeignKey('rule.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )


class Rule(IDMixin, Base):

    '''Rules for permissions and authorizations
    '''

    name = Column(String(32))
    groups = relationship("Group",
                          secondary=groups_rules, backref='rules')

