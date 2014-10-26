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


shots_sequences = Table("shots_sequences", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                      Column("sequence_id", Integer, ForeignKey(
                          "sequence.id"), primary_key=True)
                      )

shot_scene = Table("shot_scene", Base.metadata,
                   Column('id', Integer, primary_key=True),
                   Column(
                       "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                   Column(
                       "scene_id", Integer, ForeignKey("scene.id"), primary_key=True)
                   )


class Shot(IDMixin, Base):

    """Shot data
    """
    scenes = relationship('Scene', secondary='shot_scene', backref='shots')
    cut_in = Column(Integer, default=1)
    cut_out = Column(Integer)
    name = Column(String(64), nullable=False)  # shot6
    code = Column(String(64))  # SHOO1
    project_id = Column(Integer, ForeignKey("project.id"))
