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

import bz2
import ujson as json
import base64
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, db_files_path, getUUID
import os

class Report(IDMixin, Base):

    '''All reports will be saved here
    '''
    data = deferred(Column(Text, nullable=False))  # load on access
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))

    def __init__(self, data):
        self.data = data

    @validates('data')
    def compress_body(self, key, data):
        self.uuid = getUUID()
        c = bz2.compress(data)
        #result = base64.encodestring(c)
        with open(os.path.join(db_files_path, self.uuid), 'wb') as f:
            f.write(c)
        return self.uuid

    @property
    def body(self):
        with open(os.path.join(db_files_path, self.uuid), 'rb') as f:
            data = bz2.decompress(f.read())
        return data

