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
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base
from utils.fagit import GIT
from db import Session
from . import fdb
import uuid
from opensource.contenttype import contenttype
from utils.defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS

users_assets = Table('users_assets', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('asset_id', Integer, ForeignKey('asset.id'))
                     )

assets_assets = Table('assets_assets', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('asset_a_id', Integer, ForeignKey('asset.id')),
                      Column('asset_b_id', Integer, ForeignKey('asset.id'))
                      )


class Asset(IDMixin, Base):

    '''Groups for membership management
    '''
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    key = Column(String(32), nullable=False)
    name = Column(String(64))
    fullname = Column(String(256))
    description = Column(String(512))
    # information about this file. usually using identify command
    fileinfo = Column(String(512))
    # thmb = Column(String(64))  ##thmbnail image id in riak
    # pst = Column(String(64)) #poster image id in riak
    # preview = Column(String(256)) #preview video url
    ext = Column(String(32))
    content_type = Column(String(64))
    version = Column(Integer, default=1)  # asset versioning
    task_id = Column(String(64))  # celery post processing task id
    ready = Column(Boolean, default=False)  # post processing
    period = relationship("Date", uselist=False)
    users = relationship('User', backref='assets', secondary='users_assets')
    owner = relationship('User', backref='owning_assets')
    modifiers = relationship(
        'User', viewonly=True,  backref='modifying_assets', secondary='users_assets')
    repository = relationship('Repository', backref='assets')
    path = Column(String(512))  # relative to collection path, including name
    repository_id = Column(Integer, ForeignKey('repository.id'))
    owner_id = Column(Integer, ForeignKey('user.id'))
    #parent_id = Column(Integer, ForeignKey("asset.id"))
    asset_id = Column(Integer, ForeignKey("asset.id"))
    attachments = relationship("Asset", secondary=assets_assets,
                               primaryjoin=id == assets_assets.c.asset_a_id,
                               secondaryjoin=id == assets_assets.c.asset_b_id,
                               backref='attached_to')

    collection_id = Column(
        Integer, ForeignKey('collection.id'), nullable=False)
    account = relationship("Account", backref='assets')
    tgs = relationship("Tag", backref='assets')
    tags = association_proxy('tgs', 'name')

    @validates('name')
    def check_name(self, key, name):
        return name

    @validates('fullname')
    def find_type(self, key, fullname):
        self.content_type = contenttype(fullname)
        return fullname

    @validates('collection_id')
    def check_file(self, key, collection_id):
        if not os.path.isfile(self.full_path):
            raise ValueError(
                'Asset %s: *%s* is not available on Storage!' % (self.key, self.full_path))

        return collection_id

    @validates('version')
    def commit(self, key, data):
        from tasks import addFileToGit
        from tasks import identify, generateVideoThumbnail, generateVideoPreview, generateImageThumbnail
        if self.uuid:
            addFileToGit(self.full_path, self.uuid, data)
        if self.id and self.uuid:
            if self.content_type.split('/')[0] == 'video':
                generateVideoPreview.delay(self.full_path, data, self.uuid)
                newThumb = generateVideoThumbnail.delay(
                    self.full_path, self.uuid, data)
                newPoster = generateVideoThumbnail.delay(
                    self.full_path, self.uuid, data, 720, 480, 'poster')  # hd480
            if self.content_type.split('/')[0] == 'image' or self.content_type.split('/')[1] in ['pdf']:
                poster = generateImageThumbnail.delay(
                    self.full_path, data, 720, 480, self.id, 'poster')
                newThumb = generateImageThumbnail.delay(
                    self.full_path, data, 146, 110, self.id, 'thmb')

        return data

    @hybrid_property
    def full_path(self):
        if not self.ext:
            ext = ''
        else:
            ext = '.' + self.ext
        result = os.path.join(self.collection.repository.path,
                              self.collection.path,
                              self.fullname)

        return result

    @hybrid_property
    def git_tags(self):
        from tasks import getTags
        if self.uuid and self.full_path:
            result = getTags(self.full_path, self.uuid)
        return result

    @property
    def thumbnail(self):
        fmt = 'png'
        fid = self.uuid + '_thmb_' + str(self.version)
        result = os.path.join('uploads', fid + '.' + fmt)
        if os.path.isfile(os.path.join(public_upload_folder, fid + '.' + fmt)):
            return result

    @property
    def preview(self):
        fid = self.uuid + '_preview_' + str(self.version)
        fmt = 'ogv'
        result = os.path.join('uploads', fid + '.' + fmt)
        if os.path.isfile(os.path.join(public_upload_folder, fid + '.' + fmt)):
            return result

    @property
    def poster(self):
        fmt = 'png'
        fid = self.uuid + '_poster_' + str(self.version)
        result = os.path.join('uploads', fid + '.' + fmt)
        if os.path.isfile(os.path.join(public_upload_folder, fid + '.' + fmt)):
            return result

    @property
    def url(self):
        return os.path.join(os.path.basename(self.collection.repository.path),
                            self.collection.path, self.fullname)


def AfterAssetCreationFuncs(mapper, connection, target):
    '''Some operations after getting ID'''
    from tasks import identify, generateVideoThumbnail, generateVideoPreview, generateImageThumbnail
    from tasks import addFileToGit
    session = Session()
    Target = session.query(Asset).filter_by(id=target.id).first()
    addFileToGit(Target.full_path, Target.uuid, Target.version)
    identify.delay(Target.full_path, Target.id)

    # videos using ffmpeg
    if Target.content_type.split('/')[0] == 'video':
        generateVideoPreview.delay(
            Target.full_path, Target.version, Target.uuid)
        newThumb = generateVideoThumbnail.delay(
            Target.full_path, Target.uuid, Target.version)
        newPoster = generateVideoThumbnail.delay(Target.full_path, Target.uuid, Target.version,
                                                 720, 480, 'poster')  # hd480

    if Target.content_type.split('/')[0] == 'image' or Target.content_type.split('/')[1] in ['pdf']:
        poster = generateImageThumbnail.delay(Target.full_path,
                                              Target.version, 720, 480, Target.id, 'poster')
        newThumb = generateImageThumbnail.delay(Target.full_path, Target.version,
                                                146, 110, Target.id, 'thmb')

    session.commit()
    session.close()


def before_delete(mapper, connection, target):
    if os.path.isfile(target.full_path):
        try:
            os.remove(full_path)
        except:
            pass


event.listen(Asset, 'after_insert', AfterAssetCreationFuncs)
event.listen(Asset, 'before_delete', before_delete)
