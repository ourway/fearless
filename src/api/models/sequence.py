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

shots_sequences = Table("shots_sequences", Base.metadata,
                        Column('id', Integer, primary_key=True),
                        Column(
                            "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                        Column("sequence_id", Integer, ForeignKey(
                            "sequence.id"), primary_key=True)
                        )


sequences_accounts = Table("sequences_accounts", Base.metadata,
                           Column('id', Integer, primary_key=True),
                           Column(
                               "sequence_id", Integer, ForeignKey("sequence.id"), primary_key=True),
                           Column(
                               "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                           )

sequences_tags = Table("sequences_tags", Base.metadata,
                       Column('id', Integer, primary_key=True),
                       Column(
                           "sequence_id", Integer, ForeignKey("sequence.id"), primary_key=True),
                       Column(
                           "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                       )


class Sequence(IDMixin, Base):

    number = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)  # sequence1
    code = Column(String(64), nullable=False)  # SEQ1
    note = Column(String(512))  # task note
    asset_id = Column(Integer, ForeignKey("asset.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    collection = relationship("Collection", backref='sequence')
    preview = relationship("Asset", backref='sequence')
    shots = relationship('Shot', backref='sequences',
                         secondary='shots_sequences')
    period = relationship("Date", uselist=False)
    acns = relationship(
        "Account", backref='sequences', secondary="sequences_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='sequences', secondary="sequences_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    @validates('number')
    def _assign_name_code(self, key, data):
        self.name = 'sequence_%s' % str(data).zfill(3)
        self.code = 'SEQ_%s' % str(data).zfill(3)
        return data
