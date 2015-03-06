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
    def load_schema(self, key, schema):
        try:
            collection_data = self.parseScheme(schema)
            if collection_data:
                self.createChildren(collection_data)
            return schema
        except ValueError:
            pass

    @validates('template')
    def read_template(self, key, template):
        try:
            collection_data = self.parseTemplate(template)
            if collection_data:
                self.createChildren(collection_data)
            return template
        except ValueError:
            pass



    @validates('parent_id')
    def okok(self, key, data):
        self.create_and_update_path(data)
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
    def BeforeDeleteFuncs(mapper, connection, self):
        print 'deleting collection %s' % self.id
        try:
            shutil.rmtree(self.url)
        except Exception, e:
            print e

    def create_and_update_path(self, parent_id):
        from flib.models import Repository, Collection
        repository = session.query(Repository).filter_by(id=self.repository_id).scalar()
        parent = session.query(Collection).filter_by(id=parent_id).scalar()
        if parent and not parent.path in self.path:
            self.path = os.path.join(parent.path, self.path)
        self.url = os.path.join(repository.path, self.path)  ## important
        if not os.path.isdir(self.url):
            os.makedirs(self.url)
        default_thmb = os.path.join(
            os.path.dirname(__file__), '../templates/icons/asset_thumb.png')
        dest = os.path.join(self.url, 'thumb.png')
        main_thumb = os.path.join(
            os.path.dirname(__file__), '../templates/icons/%s.png' % self.name.lower())

        thmb = default_thmb
        if os.path.isfile(main_thumb):
            thmb = main_thumb
        if not os.path.isfile(dest):
            shutil.copyfile(thmb, dest)

    def parseScheme(self, schema):
        collection = defaultdict(list)
        return json.loads(self.schema)


    def parseTemplate(self, template):
        templateFile = os.path.join(
                os.path.dirname(__file__), '../templates/collection_templates.json')
        return json.loads(
                open(templateFile).read()).get(template)


    def createChildren(self, collection):
        if collection.get('folders'):
            generated = {}
            self.container = False
            self.holdAssets = False

            for folder in collection.get('folders'):
                newFolder = os.path.join(
                    self.url, folder)
                if not os.path.isdir(newFolder):
                    try:
                        os.makedirs(newFolder)
                    except OSError:
                        pass
                newCollectionName = os.path.basename(folder).title()
                for part in folder.split('/'):
                    container = False
                    holdAssets = False
                    index = folder.split('/').index(part)
                    if index == len(folder.split('/')) - 1:
                        container = False
                        holdAssets = True
                    if len(folder.split('/')) == 1:
                        container = True
                        holdAssets = False

                    part = part.strip()
                    tn = folder.split('/').index(part)
                    tc = '@@'.join(folder.split('/')[:tn + 1])
                    partPath = os.path.join(self.url,  tc.replace('@@', '/'))

                    if not generated.get(tc):
                        newCollection = Collection(name=newCollectionName, path=part,
                                                   repository_id=self.repository_id,
                                                   container=container, holdAssets=holdAssets)
                        #session.add(newCollection)
                        if tn:
                            tcm = '@@'.join(folder.split('/')[:tn])
                            newCollection.parent = generated.get(tcm)
                        else:
                            newCollection.parent = self
                        generated[tc] = newCollection
                        if 'seq_' in part.lower():
                            part = 'sequence'
                        tdest = os.path.join(partPath, 'thumb.png')
                        tsrc = os.path.join(
                            os.path.dirname(__file__), '../templates/icons/%s.png' % part.lower())
                        if not os.path.isfile(tsrc):
                            tsrc = os.path.join(os.path.dirname(__file__), '../templates/icons/data.png')
                        shutil.copyfile(tsrc, tdest)

        if collection.get('copy'):
            for c in collection.get('copy'):
                src = os.path.join(
                    os.path.dirname(__file__), '../templates/%s' % collection.get('copy')[c])
                dest = os.path.join(
                    self.url, c)

                if os.path.isfile(src):
                    shutil.copyfile(src, dest)


    @classmethod
    def __declare_last__(cls):
        pass
        event.listen(cls, 'before_delete', cls.BeforeDeleteFuncs)









#@event.listens_for(session, 'before_flush')
#def receive_before_flush(session, flush_context, instances):
#    pass
#    #session.commit()

