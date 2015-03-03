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
import bz2
import json as json
import base64
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from flib.models.mixin import IDMixin, Base, getUUID
from flib.models.helpers import tag_maker
from . import rdb

user_documents = Table('user_documents', Base.metadata,
                       Column('user_id', Integer, ForeignKey("user.id"),
                              primary_key=True),
                       Column('document_id', Integer, ForeignKey("document.id"),
                              primary_key=True)
                       )


documents_tags = Table("documents_tags", Base.metadata,
                       Column('id', Integer, primary_key=True),
                       Column(
                           "document_id", Integer, ForeignKey("document.id"), primary_key=True),
                       Column(
                           "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                       )


class Document(IDMixin, Base):

    """Implements o simple Document for assets and other docs
    """
    title = Column(String(256), unique=True)
    data = deferred(Column(Text, nullable=False))  # load on access
    user_id = Column(Integer, ForeignKey("user.id"))
    asset_id = Column(Integer, ForeignKey("asset.id"))
    author = relationship("User", backref='documents', uselist=False)
    editors = relationship(
        "User", backref='edited_documents', secondary=user_documents)
    asset = relationship("Asset", backref='documents')
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project", backref='documents')
    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship("Task", backref='documents')
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship("Account", backref='documents')
    client_id = Column(Integer, ForeignKey('client.id'))
    client = relationship("Client", backref='documents')
    shot_id = Column(Integer, ForeignKey('shot.id'))
    shot = relationship("Shot", backref='documents')
    sequence_id = Column(Integer, ForeignKey('sequence.id'))
    review_id = Column(Integer, ForeignKey('review.id'))
    sequence = relationship("Sequence", backref='documents')
    period = relationship("Date", uselist=False)
    tgs = relationship("Tag", backref='documents', secondary="documents_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    def __init__(self, data, *args, **kw):
        self.data = data


    @validates('data')
    def save_data_in_riak(self, key, data):
        self.uuid = getUUID()
        newReportObject = rdb.new(self.uuid, data.encode('utf-8'))
        newReportObject.store()
        return self.uuid

    @property
    def body(self):
        dataObject = rdb.get(self.uuid)
        return dataObject.data
