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

#from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from mixin import IDMixin, Base
import ujson as json  # for schema validations

from utils.fagit import GIT


class Collection(IDMixin, Base):

    '''All reports will be saved here
    '''
    schema = deferred(Column(Text))  # load on access
    name = Column(String(128), nullable=False)
    template = Column(String(64))
    path = Column(String(512))  # relative to repo path path
    repository_id = Column(
        Integer, ForeignKey('repository.id'), nullable=False)
    assets = relationship('Asset', backref='collection')

    @validates('schema')
    def load_json(self, key, schema):
        try:
            data = json.loads(schema)
            return schema
        except ValueError:
            pass

    @hybrid_property
    def archive(self):
        collection_path = os.path.join(
            self.repository.path, self.path or '', self.name)
        git = GIT('.', wt=collection_path)
        return git.archive()
