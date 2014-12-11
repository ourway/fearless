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
from utils.fagit import GIT

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from mixin import IDMixin, Base
from collections import defaultdict
from mako.template import Template
import ujson as json  # for collection data validation and parsing


class Repository(IDMixin, Base):

    """Manages fileserver/repository related data.
    """
    name = Column(String(32), nullable=False, unique=True)
    # this is main Path
    path = Column(String(256), nullable=False, unique=True)
    windows_path = Column(String(256))
    osx_path = Column(String(256))
    ftp_path = Column(String(256))
    sftp_path = Column(String(256))
    webdav_path = Column(String(256))
    collections = relationship('Collection', backref='repository')
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship('Project', backref='repositories')

    @validates('path')
    def create_folders(self, key, path):
        if not os.path.isdir(path):
            os.makedirs(path)
        readme = os.path.join(path, 'fearless.rst')
        with open(readme, 'wb') as f:
            f.write('welcome to Fearless repository.')
        #GIT(readme).add('repo *%s* created successfully' % self.name)
        return path

    @validates('collections')
    def check_collection_data(self, key, data):
        if data.path:
            collection_path = os.path.join(self.path, data.path)
            if not os.path.isdir(collection_path):
                os.makedirs(collection_path)

        collection = defaultdict(list)
        if data.schema:
            collection = json.loads(data.schema)
        elif data.template:
            templateFile = os.path.join(
                os.path.dirname(__file__), '../templates/collection_templates.json')
            collection = json.loads(
                open(templateFile).read()).get(data.template)
        if collection:
            # print collection.get('folders')
            for folder in collection.get('folders'):
                newFolder = os.path.join(
                    self.path, data.path or self.path, data.name, folder)
                if not os.path.isdir(newFolder):
                    try:
                        os.makedirs(newFolder)
                    except OSError:
                        pass
            for each in collection.get('files'):
                newFile = os.path.join(
                    self.path, data.path or self.path, data.name, each)
                if not os.path.isfile(newFile):
                    with open(newFile, 'w') as f:
                        tempname = collection.get('files').get(each)
                        templateFile = os.path.join(
                            os.path.dirname(__file__), '../templates/%s' % tempname)
                        if os.path.isfile(templateFile):
                            template = Template(filename=templateFile)
                            f.write(template.render(reponame=self.name, project=self.project.name,
                                                    id=data.id, collection=data.name))
                        pass
            message = 'Added: files to collection:*%s* of repo:*%s*' % (
                data.name, self.name)

            for each in collection.get('ignore'):
                with open(os.path.join(self.path, data.path or self.path, data.name,
                                       '.gitignore'), 'a+') as gitignore:
                    gitignore.writelines(each + '\n')

            collection_git = GIT(
                '.', wt=os.path.join(self.path, data.path or self.path, data.name))
            collection_git.add(message)
            #collection_git.tag('start')

            '''Add these collection folders to main repo gitignore.'''
            with open(os.path.join(self.path, '.gitignore'), 'a+') as repoignore:
                if data.path:
                    repoignore.write('%s/%s/\n' % (data.path, data.name))
                else:
                    repoignore.write(data.name + '/')
            #repo_git = GIT('.', wt=os.path.join(self.path))

        return data
