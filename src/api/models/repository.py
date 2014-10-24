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
from utils.fagit import GIT

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from mixin import IDMixin, Base

import ujson as json # for collection data validation and parsing


class Repository(IDMixin, Base):

    """Manages fileserver/repository related data.
    """
    name = Column(String(32), nullable=False, unique=True)
    path = Column(String(256), nullable=False, unique=True) # this is main Path
    windows_path = Column(String(256))
    osx_path = Column(String(256))
    ftp_path = Column(String(256))
    sftp_path = Column(String(256))
    webdav_path = Column(String(256))
    collections = relationship('Collection', backref='repository')

    @validates('path')
    def create_folders(self, key, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        readme = os.path.join(path, 'fearless.rst')
        with open(readme, 'wb') as f:
            f.write('welcome to Fearless repository')
        GIT(readme).add('repo *%s* created successfully' % self.name)
        return path

    @validates('collections')
    def check_collection_data(self, key, data):
        collection =  json.loads(data.schema)
        #print collection.get('folders')
        for folder in collection.get('folders'):
            newFolder = os.path.join(self.path, data.name, folder)
            if not os.path.isdir(newFolder):
                try:
                    os.makedirs(newFolder)
                except OSError:
                    pass
        for each in collection.get('files'):
            newFile = os.path.join(self.path, data.name, each)
            if not os.path.isfile(newFile):
                with open(newFile, 'w') as f: pass
        message = 'Added: files to collection:*%s* of repo:*%s*' % ( data.name, self.name)
        GIT('.', wt=os.path.join(self.path, data.name)).add()

        return data





