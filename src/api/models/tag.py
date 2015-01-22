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
from mixin import IDMixin, Base


class Tag(IDMixin, Base):

    """Used for any tag in orm
    """
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    name = Column(String(64), unique=True, nullable=False)
    description = Column(String(512))
    asset_id = Column(Integer, ForeignKey("asset.id"))
    parent_id = Column(Integer, ForeignKey('tag.id'))
    departement_id = Column(Integer, ForeignKey('departement.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    sequence_id = Column(Integer, ForeignKey('sequence.id'))
    shot_id = Column(Integer, ForeignKey('shot.id'))
    client_id = Column(Integer, ForeignKey('client.id'))
    asset_id = Column(Integer, ForeignKey('asset.id'))
    collection_id = Column(Integer, ForeignKey('collection.id'))
    task_id = Column(Integer, ForeignKey('task.id'))
    repository_id = Column(Integer, ForeignKey('repository.id'))
    version_id = Column(Integer, ForeignKey('version.id'))
    role_id = Column(Integer, ForeignKey('role.id'))
    group_id = Column(Integer, ForeignKey('group.id'))
    report_id = Column(Integer, ForeignKey('report.id'))
    document_id = Column(Integer, ForeignKey('document.id'))
    ticket_id = Column(Integer, ForeignKey('ticket.id'))
    account_id = Column(Integer, ForeignKey('account.id'))
    comment_id = Column(Integer, ForeignKey('comment.id'))
    date_id = Column(Integer, ForeignKey('date.id'))
    parent = relationship("Tag", backref="children", remote_side=[id])

    def __init__(self, data):
        self.name = data
