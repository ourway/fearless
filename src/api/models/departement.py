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


users_departements = Table('users_departements', Base.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('user_id', Integer, ForeignKey('user.id')),
                           Column(
                               'departement_id', Integer, ForeignKey('departement.id'))
                           )


sequences_departements = Table('sequences_departements', Base.metadata,
                               Column('id', Integer, primary_key=True),
                               Column(
                                   'sequence_id', Integer, ForeignKey('sequence.id')),
                               Column(
                                   'departement_id', Integer, ForeignKey('departement.id'))
                               )


class Departement(IDMixin, Base):

    '''Groups for membership management
    '''
    name = Column(String(64), nullable=False)
    users = relationship(
        'User', backref='departements', secondary='users_departements')
    sequences = relationship(
        'Sequence', backref='departements', secondary='sequences_departements')
