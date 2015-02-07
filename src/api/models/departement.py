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
from mixin import IDMixin, Base, UniqueMixin
from utils.helpers import tag_maker, account_maker


sequences_departements = Table('sequences_departements', Base.metadata,
                               Column('id', Integer, primary_key=True),
                               Column(
                                   'sequence_id', Integer, ForeignKey('sequence.id')),
                               Column(
                                   'departement_id', Integer, ForeignKey('departement.id'))
                               )


shots_departements = Table('shots_departements', Base.metadata,
                           Column('id', Integer, primary_key=True),
                           Column(
                               'shot_id', Integer, ForeignKey('shot.id')),
                           Column(
                               'departement_id', Integer, ForeignKey('departement.id'))
                           )


departements_accounts = Table("departements_accounts", Base.metadata,
                              Column('id', Integer, primary_key=True),
                              Column(
                                  "departement_id", Integer, ForeignKey("departement.id"), primary_key=True),
                              Column(
                                  "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                              )

departements_tags = Table("departements_tags", Base.metadata,
                          Column('id', Integer, primary_key=True),
                          Column(
                              "departement_id", Integer, ForeignKey("departement.id"), primary_key=True),
                          Column(
                              "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                          )


class Departement(IDMixin, UniqueMixin, Base):

    '''Groups for membership management
    '''
    name = Column(String(64), nullable=False)
    period = relationship("Date", uselist=False)
    acns = relationship(
        "Account", backref='departements', secondary="departements_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship(
        "Tag", backref='departements', secondary="departements_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    @classmethod
    def unique_hash(cls, name):
        if name:
            name = name.lower()
        return name

    @classmethod
    def unique_filter(cls, query, name):
        if name:
            return query.filter(Departement.name == name.lower())
