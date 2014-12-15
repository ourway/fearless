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

from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from mixin import IDMixin, Base, getUUID
from sqlalchemy_utils import PasswordType, aggregated
from db import session, Session





class Account(IDMixin, Base):

    '''Rules for permissions and authorizations
    '''

    id = Column( Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    name = Column(String(32), nullable=False, unique=True)
    max_credit = Column(Float(precision=3), default=0)
    credit = Column(Float(precision=3), default=0)
    parent_id = Column(Integer, ForeignKey('account.id'))
    parent = relationship("Account", backref="children" ,remote_side=[id])
    #start = Column(DateTime, nullable=False, default=now)


    @validates('credit')
    def check_credit(self, key, data):
        if self.parent:
            chs = session.query(func.sum("Account.credit").label(total_credit)).filter_by(parent=parent).first()
            if chs.total_credit<=self.parent.max_credit+data:
                return data

