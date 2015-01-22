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
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base
from collections import defaultdict
import json as json  # for collection data validation and parsing


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
    project = relationship('Project', backref='repositories')
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("User", backref="ownes_repositories")
    period = relationship("Date", uselist=False)
    tgs = relationship("Tag", backref='repositories')
    tags = association_proxy('tgs', 'name')

    @validates('path')
    def create_folders(self, key, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        readme = os.path.join(path, 'fearless.rst')
        with open(readme, 'wb') as f:
            f.write('welcome to Fearless repository.')
        #GIT(readme).add('repo *%s* created successfully' % self.name)
        return path
