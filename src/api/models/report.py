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
import base64
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base


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
        c = bz2.compress(data)
        result = base64.encodestring(c)
        return result

    @property
    def body(self):
        b = base64.decodestring(self.data)
        return bz2.decompress(b)
