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


class Tag(IDMixin, Base):

    """Used for any tag in orm
    """
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    name = Column(String(64), unique=True, nullable=False)
    description = Column(String(512))
    parent_id = Column(Integer, ForeignKey('tag.id'))
    parent = relationship("Tag", backref="children", remote_side=[id])

    def __init__(self, data, *args, **kw):
        self.name = data
