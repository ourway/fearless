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
from mixin import IDMixin, Base


versions_tags = Table("versions_tags", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "version_id", Integer, ForeignKey("version.id"), primary_key=True),
                      Column(
                          "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                      )


class Version(IDMixin, Base):

    """Holds information about the created versions (files) for a class:`.Task`
    """
    take_name = Column(String(256), nullable=False)
    number = Column(Integer, default=1)
    is_published = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey('task.id'))
    tgs = relationship("Tag", backref='versions', secondary="versions_tags")
    tags = association_proxy('tgs', 'name')
    #asset_id = Column(Integer, ForeignKey('task.id'))
