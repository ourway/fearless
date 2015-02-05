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
from mixin import IDMixin, Base, db_files_path, getUUID
from sqlalchemy.ext.associationproxy import association_proxy
from utils.helpers import tag_maker
import os
from . import rdb




reports_tags = Table("reports_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "report_id", Integer, ForeignKey("report.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


class Report(IDMixin, Base):

    '''All reports will be saved here
    '''
    data = deferred(Column(Text, nullable=False))  # load on access
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    asset_id = Column(Integer, ForeignKey('asset.id'))
    asset = relationship('Asset', backref='reports')
    client_id = Column(Integer, ForeignKey('client.id'))
    client = relationship("Client", backref='reports')
    shot_id = Column(Integer, ForeignKey('shot.id'))
    shot = relationship("Shot", backref='reports')
    sequence_id = Column(Integer, ForeignKey('sequence.id'))
    sequence = relationship("Sequence", backref='reports')
    task_id = Column(Integer, ForeignKey("task.id"))
    due = relationship("Date")
    tgs = relationship("Tag", backref='reports', secondary="reports_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)


    def __init__(self, data, *args, **kw):
        self.data = data

    @validates('data')
    def save_data_in_riak(self, key, data):
        self.uuid = getUUID()
        #c = bz2.compress(data)
        newReportObject = rdb.new(self.uuid, {'body': data})
        #result = base64.encodestring(c)
        # with open(os.path.join(db_files_path, self.uuid), 'wb') as f:
        #    f.write(c)
        newReportObject.store()
        return self.uuid

    @property
    def body(self):
        # with open(os.path.join(db_files_path, self.uuid), 'rb') as f:
        #    data = bz2.decompress(f.read())
        dataObject = rdb.get(self.uuid)
        if dataObject.data:
            return dataObject.data.get('body')
