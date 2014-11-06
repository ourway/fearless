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
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from mixin import IDMixin, Base
from utils.fagit import GIT

users_assets = Table('users_assets', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('asset_id', Integer, ForeignKey('asset.id'))
                     )


class Asset(IDMixin, Base):

    '''Groups for membership management
    '''
    key = Column(String(32), nullable=False, unique=True)
    name = Column(String(128))
    ext = Column(String(32))
    content_type = Column(String(64))
    version = Column(Integer, default=1)  ## asset versioning
    task_id = Column(String(64))  # celery post processing task id
    ready = Column(Boolean, default=False)  # post processing
    users = relationship('User', backref='assets', secondary='users_assets')
    modifiers = relationship('User', backref='modifying_assets', secondary='users_assets')
    repository = relationship('Repository', backref='assets')
    path = Column(String(512))  # relative to collection path, including name
    repository_id = Column(Integer, ForeignKey('repository.id'))
    collection_id = Column(
        Integer, ForeignKey('collection.id'), nullable=False)


    @validates('collection_id')
    def check_file(self, key, collection_id):
        if not os.path.isfile(self.full_path):
            raise ValueError(
                'Asset %s:* %s * is not available on Storage!' % (self.key, self.full_path))

        return collection_id

    @validates('version')
    def commit(self, key, data):
        wt = os.path.join(self.collection.repository.path, self.collection.path)
        git = GIT(self.full_path, wt=wt)
        git.add('Asset *%s*' % self.name, version=data)
        return data

    @hybrid_property
    def full_path(self):
        if not self.ext:
            ext = ''
        else:
            ext = '.' + self.ext
        result = os.path.join(self.collection.repository.path,
                            self.collection.path,
                            self.path or '', self.name)

        return result

    @property
    def url(self):
        return os.path.join(os.path.basename(self.collection.repository.path),
                            self.collection.path, self.path or '', self.name)
