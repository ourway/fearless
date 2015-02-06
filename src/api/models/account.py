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

from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, getUUID, UniqueMixin
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.ext.associationproxy import association_proxy
from utils.helpers import tag_maker
from db import Session
session = Session()



accounts_tags = Table("accounts_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "account_id", Integer, ForeignKey("account.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )



class Account(IDMixin, UniqueMixin, Base):

    '''Rules for permissions and authorizations
    '''

    # over-ride mixin version. because of remote_side
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)
    description = Column(Text())
    name = Column(String(32), nullable=False, unique=True)
    max_credit = Column(Float(precision=3), default=0)
    credit = Column(Float(precision=3), default=0)
    parent_id = Column(Integer, ForeignKey('account.id'))
    parent = relationship("Account", backref="children", remote_side=[id])
    period = relationship("Date", uselist=False)
    tgs = relationship("Tag", backref='accounts', secondary="accounts_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    #start = Column(DateTime, nullable=False, default=now)




    @classmethod
    def unique_hash(cls, name):
        if name:
            name = name.lower()
        return name

    @classmethod
    def unique_filter(cls, query, name):
        if name:
            return query.filter(Account.name == name.lower())

    @validates('credit')
    def check_credit(self, key, data):
        if self.parent:
            chs = session.query(func.sum("Account.credit").label(total_credit)).filter_by(
                parent=parent).first()
            session.close()
            if chs.total_credit <= self.parent.max_credit + data:
                return data

