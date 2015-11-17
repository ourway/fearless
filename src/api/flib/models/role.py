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
from sqlalchemy.ext.associationproxy import association_proxy
from flib.models.mixin import IDMixin, Base, getUUID, UniqueMixin
from flib.models.helpers import tag_maker


roles_tags = Table("roles_tags", Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column(
                       "role_id", Integer, ForeignKey("role.id"), primary_key=True),
                   Column(
                       "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                   )


class Role(IDMixin, UniqueMixin, Base):

    '''Rules for permissions and authorizations
    '''

    name = Column(String(32), nullable=False, unique=True)
    tgs = relationship("Tag", backref='roles', secondary="roles_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    def __init__(self, name):
        self.name = name

    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Role.name == name)
