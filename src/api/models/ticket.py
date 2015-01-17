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
from mixin import IDMixin, Base


class Ticket(IDMixin, Base):

    """Tickets are the way of reporting errors or asking for changes.
    """
    project_id = Column(Integer, ForeignKey("project.id"))
    name = Column(String(64), nullable=False)
    body = deferred(Column(Text))
    period = relationship("Date", uselist=False)
    tgs = relationship("Tag", backref='tickets')
    tags = association_proxy('tgs', 'name')

    def __init__(self, name):
        self.name = name
