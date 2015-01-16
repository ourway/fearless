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
from mixin import IDMixin, Base


client_users = Table('client_users', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('client_id', Integer, ForeignKey('client.id')),
                     Column('user_id', Integer, ForeignKey('user.id'))
                     )


class Client(IDMixin, Base):

    '''The Client (e.g. a company) which users may be part of.
    '''
    name = Column(String(64), unique=True, nullable=False)
    users = relationship('User', backref='companies', secondary='client_users')
    period = relationship("Date", uselist=False)
    account = relationship("Account", backref='client')
