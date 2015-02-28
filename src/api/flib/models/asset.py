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
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from flib.models.mixin import IDMixin, Base
from flib.utils.fagit import GIT
from flib.models.helpers import tag_maker, account_maker
from flib.models import fdb
import uuid
from flib.opensource.contenttype import contenttype
from flib.utils.defaults import public_upload_folder, public_repository_path, GIT_folder, ASSETS

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


aasets_accounts = Table("assets_accounts", Base.metadata,
                        Column('id', Integer, primary_key=True),
                        Column(
                            "asset_id", Integer, ForeignKey("asset.id"), primary_key=True),
                        Column(
                            "account_id", Integer, ForeignKey("account.id"), primary_key=True)
                        )

assets_tags = Table("assets_tags", Base.metadata,
                    Column('id', Integer, primary_key=True),
                    Column(
                        "asset_id", Integer, ForeignKey("asset.id"), primary_key=True),
                    Column(
                        "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
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
    content_size = Column(Integer)  # asset size
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
                               single_parent=True,
                               primaryjoin=id == assets_assets.c.asset_a_id,
                               secondaryjoin=id == assets_assets.c.asset_b_id,
                               backref="attached_to", cascade="all, delete, delete-orphan")

    collection_id = Column(
        Integer, ForeignKey('collection.id'), nullable=False)
    acns = relationship(
        "Account", backref='assets', secondary="assets_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='assets', secondary="assets_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)

    @validates('name')
    def check_name(self, key, name):
        return name

    @validates('content_type')
    def add_a_tag_based_on_contenttpye(self, key, ct):
        if ct:
            self.tags.append(ct.split('/')[0])
            self.tags.append(ct.split('/')[-1].split(';')[0])
            if 'x-markdown' in self.tags:
                self.tags.append('document')

        return ct

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
        from flib.tasks import addFileToGit
        from flib.tasks import identify, generateVideoThumbnail, generateVideoPreview, generateImageThumbnail
        if self.uuid:
            addFileToGit.delay(self.full_path, self.uuid, data)
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
        from flib.tasks import getTags
        if self.uuid and self.full_path:
            result = getTags(self.full_path, self.uuid)
        return result

    @hybrid_property
    def collection_name(self):
        return self.collection.name

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
        fmt = 'mp4'
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



    @staticmethod
    def before_insert(mapper, connection, target):
        target.content_size = os.path.getsize(target.full_path)

    @staticmethod
    def AfterAssetCreationFuncs(mapper, connection, target):
        '''Some operations after getting ID'''
        from flib.tasks import identify, generateVideoThumbnail, generateVideoPreview, generateImageThumbnail
        from flib.tasks import addFileToGit
        addFileToGit.delay(target.full_path, target.uuid, target.version)
        identify.delay(target.full_path, target.id)

        # videos using ffmpeg
        if target.content_type.split('/')[0] == 'video':
            generateVideoPreview.delay(
                target.full_path, target.version, target.uuid)
            newThumb = generateVideoThumbnail.delay(
                target.full_path, target.uuid, target.version)
            newPoster = generateVideoThumbnail.delay(target.full_path, target.uuid, target.version,
                                                     720, 480, 'poster')  # hd480

        if target.content_type.split('/')[0] == 'image' or target.content_type.split('/')[1] in ['pdf']:
            poster = generateImageThumbnail.delay(target.full_path,
                                                  target.version, 720, 480, target.id, 'poster')
            newThumb = generateImageThumbnail.delay(target.full_path, target.version,
                                                    146, 110, target.id, 'thmb')


    @staticmethod
    def before_update(mapper, connection, target):
        target.content_size = os.path.getsize(target.full_path)


    @staticmethod
    def before_delete(mapper, connection, target):
        print 'deleting Asset  %s' % target.id
        if os.path.isfile(target.full_path):
            try:
                os.remove(target.full_path)
            except Exception, e:
                print e
        for i in [target.preview, target.poster]:
            if i:
                ipath =  os.path.join(os.path.dirname(public_upload_folder), i)
                if os.path.isfile(ipath):
                    os.remove(ipath)

        afolder = os.path.join(ASSETS, target.uuid)
        gitfolder = os.path.join(GIT_folder, target.uuid)
        for folder in [afolder, gitfolder]:
            if folder and os.path.isdir(folder):
                try:
                    shutil.rmtree(folder)
                except Exception, e:
                    print e
        

            

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'after_insert', cls.AfterAssetCreationFuncs)
        event.listen(cls, 'before_delete', cls.before_delete)
        event.listen(cls, 'before_update', cls.before_update)
        event.listen(cls, 'before_insert', cls.before_insert)
