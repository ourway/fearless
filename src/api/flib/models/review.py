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
from flib.models.mixin import IDMixin, Base
from flib.models.helpers import tag_maker, account_maker


review_tags = Table("review_tags", Base.metadata,
                    Column('id', Integer, primary_key=True),
                    Column(
                        "review_id", Integer, ForeignKey("review.id"), primary_key=True),
                    Column(
                        "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                    )


class Review(IDMixin, Base):

    '''The review class for a task.
    '''
    task_id = Column(Integer, ForeignKey('task.id'))
    asset_id = Column(Integer, ForeignKey('asset.id'))
    reviewer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    #task = relationship("Task", backref='reviews', uselist=False)
    reviewer = relationship("User", backref='reviewed')
    tgs = relationship("Tag", backref='reviews', secondary="review_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)
    cnt = relationship("Document", backref='review', uselist=False)
    content = association_proxy('cnt', 'body')
