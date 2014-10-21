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
from sqlalchemy.ext.hybrid import hybrid_property
from mixin import IDMixin, Base


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
    task_id = Column(String(64))  # celery post processing task id
    ready = Column(Boolean, default=False)  # celery post processing task id
    users = relationship('User', backref='assets', secondary='users_assets')
    repository = relationship('Repository', backref='assets')
    path = Column(String(512))
    repository_id = Column(Integer, ForeignKey('repository.id'))


