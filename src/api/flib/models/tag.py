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
from flib.models.mixin import IDMixin, Base, UniqueMixin


class Tag(IDMixin, UniqueMixin, Base):

    """Used for any tag in orm
    """

    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    name = Column(String(32), unique=True, nullable=False)
    description = Column(String(512))
    parent_id = Column(Integer, ForeignKey('tag.id'))
    parent = relationship("Tag", backref="children", remote_side=[id])

    @classmethod
    def unique_hash(cls, name):
        if name:
            name = name.lower()
        return name

    @classmethod
    def unique_filter(cls, query, name):
        if name:
            return query.filter(Tag.name == name.lower())
