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

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base, UniqueMixin
from utils.helpers import tag_maker


groups_roles = Table('group_roles', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('role_id', Integer, ForeignKey('role.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )


groups_tags = Table("groups_tags", Base.metadata,
                    Column('id', Integer, primary_key=True),
                    Column(
                        "group_id", Integer, ForeignKey("group.id"), primary_key=True),
                    Column(
                        "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                    )


class Group(IDMixin, UniqueMixin, Base):

    '''Groups for membership management
    '''
    name = Column(String(32), nullable=False, unique=True)
    typ = Column(String(32), nullable=False, default='private')
    rls = relationship("Role",
                       secondary=groups_roles, backref='groups')
    roles = association_proxy('rls', 'name')
    tgs = relationship("Tag", backref='groups', secondary="groups_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    def __init__(self, name, role=None, typ='private'):
        self.name = name
        self.typ = typ
        if role:
            self.roles.append(role)

    @classmethod
    def unique_hash(cls, name):
        if name:
            name = name.lower()
        return name

    @classmethod
    def unique_filter(cls, query, name):
        if name:
            return query.filter(Group.name == name.lower())
