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
from sqlalchemy.orm.session import Session as SessionBase
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


    @validates('repository_id')
    def updateUrl(self, key, data):
        #if self.path:
        #    self.url = os.path.join(repo.path, self.path)
        return data

    @validates('schema')
    def load_json(self, key, schema):
        try:
            data = json.loads(schema)
            return schema
        except ValueError:
            pass

    @validates('parent_id')
    def update_path(self, key, data):
        parent = session.query(Collection).filter_by(id=data).first()
        if parent and parent.path not in self.path:
            newpath = os.path.join(parent.path, self.path)
            self.path = newpath
        return data

    @validates('repository')
    def validate_repo(self, key, data):
        print data
        return data


    @validates('path')
    def check_path(self, key, data):
        self.name = os.path.basename(data).title()
        if self.repository:
            self.url = os.path.join(self.repository.path, data)
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












def createStandards(target, session):
    '''Some operations after getting ID'''
    repository = target.repository
    if not repository:
        repository = session.query(Repository).filter_by(id=target.repository_id).first()

    if not repository:
        return

    if target.path:
        collection_path = os.path.join(repository.path, target.path)
        if not os.path.isdir(collection_path):
            os.makedirs(collection_path)
        thmb = os.path.join(
            os.path.dirname(__file__), '../templates/icons/asset_thumb.png')
        dest = os.path.join(collection_path, 'thumb.png')
        if not os.path.isfile(dest):
            shutil.copyfile(thmb, dest)

    collection = defaultdict(list)
    if target.schema:
        collection = json.loads(target.schema)
    elif target.template:
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/collection_templates.json')
        collection = json.loads(
            open(templateFile).read()).get(target.template)

    if collection:

        # print collection.get('folders')
        if collection.get('folders'):
            generated = {}
            target.container = False
            target.holdAssets = False

            for folder in collection.get('folders'):
                newFolder = os.path.join(
                    repository.path, target.path or repository.path, folder)
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
                    partPath = os.path.join(
                        repository.path, target.path,  tc.replace('@@', '/'))

                    if not generated.get(tc):
                        newCollection = Collection(name=newCollectionName, path=part,
                                                   repository_id=repository.id,
                                                   container=container, holdAssets=holdAssets)
                        if tn:
                            tcm = '@@'.join(folder.split('/')[:tn])
                            newCollection.parent = generated.get(tcm)
                            #session.add(newCollection)
                        else:
                            newCollection.parent = target
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
                    repository.path, target.path or repository.path, c)

                if os.path.isfile(src):
                    shutil.copyfile(src, dest)








def before_flush(session, flush_context, instances):
    for i in session.new:
        if i.__tablename__ == 'collection':
            createStandards(i, session)


event.listen(SessionBase, "before_flush", before_flush)




#@event.listens_for(session, 'before_flush')
#def receive_before_flush(session, flush_context, instances):
#    pass
#    #session.commit()

