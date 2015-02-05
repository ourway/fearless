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

shots_scenes = Table("shots_scenes", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                     Column(
                         "scene_id", Integer, ForeignKey("scene.id"), primary_key=True)
                     )

shots_accounts = Table("shots_accounts", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                     Column(
                         "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                     )

shots_tags = Table("shots_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "shot_id", Integer, ForeignKey("shot.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


class Shot(IDMixin, Base):

    """Shot data
    """
    scenes = relationship('Scene', secondary='shot_scene', backref='shots')
    cut_in = Column(Integer, default=1)
    cut_out = Column(Integer)
    number = Column(Integer, nullable=False)
    name = Column(String(64), nullable=False)  # shot6
    code = Column(String(64), nullable=False)  # SHOO1
    timerate = Column(Integer, default=1)
    project_id = Column(Integer, ForeignKey("project.id"))
    asset_id = Column(Integer, ForeignKey("asset.id"))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    collection = relationship("Collection", backref='shots')
    preview = relationship("Asset", backref='shots')
    scenes = relationship("Scene", backref='shots', secondary="shots_scenes")
    period = relationship("Date", uselist=False)
    acns = relationship("Account", backref='shots', secondary="shots_accounts")
    aacounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='shots', secondary="shots_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)


    @validates('number')
    def _assign_name_code(self, key, data):
        self.name = 'shot_%s' % str(data).zfill(4)
        self.code = 'SH_%s' % str(data).zfill(4)
        return data
