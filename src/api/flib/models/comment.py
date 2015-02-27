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
from flib.models.helpers import tag_maker


comments_tags = Table("comments_tags", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "comment_id", Integer, ForeignKey("comment.id"), primary_key=True),
                      Column(
                          "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                      )


class Comment(IDMixin, Base):

    """Implements o simple Document structure for wikis and structures
    """
    item = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    tag = Column(String(64))
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref='comments')
    tgs = relationship("Tag", backref='comments', secondary="comments_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)
