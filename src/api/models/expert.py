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
from mixin import IDMixin, Base, getUUID, UniqueMixin
from utils.helpers import tag_maker, account_maker

experts_accounts = Table("experts_accounts", Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column(
                             "expert_id", Integer, ForeignKey("expert.id"), primary_key=True),
                         Column(
                             "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                         )

experts_tags = Table("experts_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "expert_id", Integer, ForeignKey("expert.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


class Expert(IDMixin, UniqueMixin, Base):

    '''Rules for permissions and authorizations
    '''

    name = Column(String(128), nullable=False, unique=True)
    acns = relationship(
        "Account", backref='expertise', secondary="experts_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='expert', secondary="experts_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    def __init__(self, name):
        self.name = name

    @classmethod
    def unique_hash(cls, name):
        return name

    @classmethod
    def unique_filter(cls, query, name):
        return query.filter(Expert.name == name)
