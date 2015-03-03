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

import os
import shutil
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event, func

#from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from flib.models.mixin import IDMixin, Base
from sqlalchemy_utils import aggregated
import ujson as json  # for schema validations
from mako.template import Template

from flib.utils.fagit import GIT
from flib.models.helpers import tag_maker
from flib.models import Repository
from flib.models.db import Session, session_factory
session = Session()
from collections import defaultdict


collections_tags = Table("collections_tags", Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column(
                             "collection_id", Integer, ForeignKey("collection.id"), primary_key=True),
                         Column(
                             "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                         )


class Collection(IDMixin, Base):

    '''All reports will be saved here
    '''
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    schema = deferred(Column(Text))  # load on access
    name = Column(String(128))
    description = Column(String(512))
    container = Column(Boolean(), default=True)  # can contain assets
    holdAssets = Column(Boolean(), default=True)  # can contain assets
    version = Column(Integer, default=1)  # asset versioning
    template = Column(String(64))
    owner_id = Column(Integer, ForeignKey('user.id'))
    parent_id = Column(Integer, ForeignKey('collection.id'))
    parent = relationship("Collection", backref=backref("children", cascade="all, delete, delete-orphan"),
                          remote_side=[id])
    owner = relationship("User", backref="ownes_collections")
    path = Column(String(512), nullable=False)  # relative to repo path path
    url = Column(String(512))  # relative to repo path path
    repository_id = Column(
        Integer, ForeignKey('repository.id'), nullable=False)
    assets = relationship(
        'Asset', backref='collection', cascade="all, delete, delete-orphan")
    tgs = relationship(
        "Tag", backref='collections', secondary="collections_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)


    @aggregated('assets', Column(Integer))
    def number_of_assets(self):
        return func.sum('1')

    @aggregated('assets', Column(Integer))
    def collection_size(self):
        from . import Asset
        return func.sum(Asset.content_size)




    @validates('schema')
    def load_json(self, key, schema):
        try:
            data = json.loads(schema)
            return schema
        except ValueError:
            pass



    @validates('repository')
    def validate_repo(self, key, data):
        return data


    @validates('path')
    def check_path(self, key, data):
        self.name = os.path.basename(data).title()
        return data

    @hybrid_property
    def archive(self):
        pass
        # collection_path = os.path.join(
        #    self.repository.path, self.path or '')
        #git = GIT('.', wt=collection_path)
        # return git.archive()
    @staticmethod
    def BeforeUserDeleteFuncs(mapper, connection, target):
        print 'deleting collection %s' % target.id
        try:
            shutil.rmtree(target.url)
        except Exception, e:
            print e


    @classmethod
    def __declare_last__(cls):
        pass
        #event.listen(cls, 'after_insert', cls.AfterUserCreationFuncs)
        event.listen(cls, 'before_delete', cls.BeforeUserDeleteFuncs)









#@event.listens_for(session, 'before_flush')
#def receive_before_flush(session, flush_context, instances):
#    pass
#    #session.commit()

