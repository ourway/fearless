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


tickets_tags = Table("tickets_tags", Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column(
                         "ticket_id", Integer, ForeignKey("ticket.id"), primary_key=True),
                     Column(
                         "tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
                     )


class Ticket(IDMixin, Base):

    """Tickets are the way of reporting errors or asking for changes.
    """
    project_id = Column(Integer, ForeignKey("project.id"))
    shot_id = Column(Integer, ForeignKey("shot.id"))
    sequence_id = Column(Integer, ForeignKey("sequence.id"))
    ticket_type = Column(String(32))
    name = Column(String(64), nullable=False)
    period = relationship("Date", uselist=False)
    tgs = relationship("Tag", backref='tickets', secondary="tickets_tags")
    tags = association_proxy('tgs', 'name')
    task_id = Column(Integer, ForeignKey('task.id'))
    asset_id = Column(Integer, ForeignKey('asset.id'))
    ticketer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    task = relationship("Task", backref='tickets', uselist=False)
    shot = relationship("Shot", backref='tickets', uselist=False)
    sequence = relationship("Sequence", backref='tickets', uselist=False)
    ticketer = relationship("User", backref='tickets')
    cnt = relationship("Document", backref='ticket', uselist=False)
    content = association_proxy('cnt', 'body')
