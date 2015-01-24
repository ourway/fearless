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

#from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base
import ujson as json  # for schema validations
from mako.template import Template

from utils.fagit import GIT
from . import Repository
from db import session, Session
from collections import defaultdict


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
    parent = relationship("Collection", backref="children", remote_side=[id])
    owner = relationship("User", backref="ownes_collections")
    path = Column(String(512), nullable=False)  # relative to repo path path
    url = Column(String(512))  # relative to repo path path
    repository_id = Column(
        Integer, ForeignKey('repository.id'), nullable=False)
    assets = relationship('Asset', backref='collection', cascade="all, delete, delete-orphan")
    tgs = relationship("Tag", backref='collections')
    tags = association_proxy('tgs', 'name')

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

    @validates('repository_id')
    def update_url(self, key, data):
        if self.path:
            repository = session.query(Repository).filter(
                Repository.id == data).first()
            self.url = os.path.join(repository.path, self.path)
        return data

    @validates('path')
    def check_path(self, key, data):
        self.name = os.path.basename(data).title()
        if self.repository_id:
            repository = session.query(Repository).filter(
                Repository.id == self.repository_id).first()
            self.url = os.path.join(repository.path, data)
        return data

    @hybrid_property
    def archive(self):
        pass
        # collection_path = os.path.join(
        #    self.repository.path, self.path or '')
        #git = GIT('.', wt=collection_path)
        # return git.archive()


def BeforeUserCreationFuncs(mapper, connection, target):
    pass


def AfterUserCreationFuncs(mapper, connection, target):
    '''Some operations after getting ID'''
    session = Session()
    repository = session.query(Repository).filter_by(
        id=target.repository_id).first()
    Target = session.query(Collection).filter_by(id=target.id).first()
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
            Target.container = False
            Target.holdAssets = False

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
                        container = True
                        holdAssets = True

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
                        else:
                            newCollection.parent_id = target.id
                        generated[tc] = newCollection
                        if 'seq_' in part.lower():
                            part = 'sequence'
                        tdest = os.path.join(partPath, 'thumb.png')
                        tsrc = os.path.join(
                            os.path.dirname(__file__), '../templates/icons/%s.png' % part.lower())
                        if os.path.isfile(tsrc):
                            shutil.copyfile(tsrc, tdest)
                        session.add(newCollection)

        if collection.get('copy'):
            for c in collection.get('copy'):
                src = os.path.join(
                    os.path.dirname(__file__), '../templates/%s' % collection.get('copy')[c])
                dest = os.path.join(
                    repository.path, target.path or repository.path, c)

                if os.path.isfile(src):
                    shutil.copyfile(src, dest)


#        if collection.get('files'):
#            for each in collection.get('files'):
#                newFile = os.path.join(
#                    repository.path, target.path or repository.path, each)
#                if not os.path.isfile(newFile):
#                    with open(newFile, 'w') as f:
#                        tempname = collection.get('files').get(each)
#                        templateFile = os.path.join(
#                            os.path.dirname(__file__), '../templates/%s' % tempname)
#                        if os.path.isfile(templateFile):
#                            template = Template(filename=templateFile)
#                            f.write(template.render(reponame=repository.name, project=repository.project.name,
# id=target.id, collection=target.name.decode('utf-8')))


#        message = 'Added: files to collection:*%s* of repo:*%s*' % (
#            target.name, repository.name)
#
#        if collection.get('ignore'):
#            for each in collection.get('ignore'):
#                with open(os.path.join(repository.path, target.path or repository.path ,
#                                       '.gitignore'), 'a+') as gitignore:
#                    gitignore.writelines(each + '\n')
#
#        collection_git = GIT(
#            '.', wt=os.path.join(repository.path, target.path or repository.path))
#        collection_git.add(message)
#        #collection_git.tag('start')
#
#        '''Add these collection folders to main repo gitignore.'''
#        with open(os.path.join(repository.path, '.gitignore'), 'a+') as repoignore:
#            if target.path:
#                repoignore.write('%s/\n' % (target.path))
#            else:
#                repoignore.write('/')
        #repo_git = GIT('.', wt=os.path.join(self.path))

    session.commit()
    session.close()


event.listen(Collection, 'after_insert', AfterUserCreationFuncs)
event.listen(Collection, 'before_insert', BeforeUserCreationFuncs)
