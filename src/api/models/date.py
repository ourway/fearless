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
from mixin import IDMixin, Base, now




class Date(IDMixin, Base):

    '''The Client (e.g. a company) which users may be part of.
    '''
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    accpeted = Column(Boolean(), default=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    task_id = Column(Integer, ForeignKey('task.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    shot_id = Column(Integer, ForeignKey('shot.id'))
    sequence_id = Column(Integer, ForeignKey('sequence.id'))
    scene_id = Column(Integer, ForeignKey('scene.id'))
    repository_id = Column(Integer, ForeignKey('repository.id'))
    collection_id = Column(Integer, ForeignKey('collection.id'))
    asset_id = Column(Integer, ForeignKey('asset.id'))
    report_id = Column(Integer, ForeignKey('report.id'))
    ticket_id = Column(Integer, ForeignKey('ticket.id'))
    account_id = Column(Integer, ForeignKey('account.id'))
    document_id = Column(Integer, ForeignKey('document.id'))
    departement_id = Column(Integer, ForeignKey('departement.id'))
    tgs = relationship("Tag", backref='dates')
    tags = association_proxy('tgs', 'name')
