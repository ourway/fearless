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

shots_sequences = Table("shots_sequences", Base.metadata,
                        Column('id', Integer, primary_key=True),
                        Column(
                            "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                        Column("sequence_id", Integer, ForeignKey(
                            "sequence.id"), primary_key=True)
                        )

class Sequence(IDMixin, Base):

    number = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)  # sequence1
    code = Column(String(64), nullable=False)  # SEQ1
    note = Column(String(512))  ## task note
    project_id = Column(Integer, ForeignKey("project.id"))
    shots = relationship( 'Sequence', backref='sequences', 
                secondary='shots_sequences')


    @validates('number')
    def _assign_name_code(self, key, data):
        self.name = 'sequence_%s' % str(data).zfill(3)
        self.code = 'SEQ_%s' % str(data).zfill(3)
        return data
