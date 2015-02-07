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
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base
from utils.helpers import tag_maker, account_maker


client_users = Table('client_users', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('client_id', Integer, ForeignKey('client.id')),
                     Column('user_id', Integer, ForeignKey('user.id'))
                     )


clients_accounts = Table("clients_accounts", Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column(
                             "client_id", Integer, ForeignKey("client.id"), primary_key=True),
                         Column(
                             "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                         )


clients_tags = Table("clients_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "client_id", Integer, ForeignKey("client.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


class Client(IDMixin, Base):

    '''The Client (e.g. a company) which users may be part of.
    '''
    name = Column(String(64), unique=True, nullable=False)
    users = relationship('User', backref='companies', secondary='client_users')
    period = relationship("Date", uselist=False)
    acns = relationship(
        "Account", backref='client', secondary="clients_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='clients', secondary="clients_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)
