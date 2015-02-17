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

import os
import shutil
from utils.fagit import GIT

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base
from collections import defaultdict
from utils.helpers import tag_maker
import json as json  # for collection data validation and parsing


repositories_tags = Table("repositories_tags", Base.metadata,
                          Column('id', Integer, primary_key=True),
                          Column(
                              "repository_id", Integer, ForeignKey("repository.id"), primary_key=True),
                          Column(
                              "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                          )


class Repository(IDMixin, Base):

    """Manages fileserver/repository related data.
    """
    name = Column(String(32), nullable=False, unique=True)
    # this is main Path
    path = Column(String(256), nullable=False, unique=True)
    windows_path = Column(String(256))
    osx_path = Column(String(256))
    ftp_path = Column(String(256))
    sftp_path = Column(String(256))
    webdav_path = Column(String(256))
    collections = relationship(
        'Collection', backref='repository', cascade="all, delete, delete-orphan")
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship('Project', backref=backref('repositories', cascade="all, delete, delete-orphan"))
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("User", backref="ownes_repositories")
    period = relationship("Date", uselist=False)
    tgs = relationship(
        "Tag", backref='repositories', secondary="repositories_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    @validates('path')
    def create_folders(self, key, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        readme = os.path.join(path, 'fearless.rst')
        with open(readme, 'wb') as f:
            f.write('welcome to Fearless repository.')
        #GIT(readme).add('repo *%s* created successfully' % self.name)
        return path


    @staticmethod
    def before_delete(mapper, connection, target):
        print 'Deleting repository %s' % target.id
        ipath = target.path
        if os.path.isdir(ipath):
            try:
                shutil.rmtree(ipath)
            except Exception, e:
                pass


    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_delete', cls.before_delete)
