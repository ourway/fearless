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

    @validates('path')
    def create_folders(self, key, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        readme = os.path.join(path, 'fearless.rst')
        with open(readme, 'wb') as f:
            f.write('welcome to Fearless repository')
        GIT(readme).add('repo "%s" created successfully' % self.name)
        return path




