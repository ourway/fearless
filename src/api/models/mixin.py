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


import datetime
import ujson as json
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from sqlalchemy_mptt.mixins import BaseNestedSets
from utils.general import setup_logger
from uuid import uuid4  # for random guid generation

now = datetime.datetime.utcnow

Base = declarative_base()
logger = setup_logger('model', 'model.log')

def get_session():
    from models import session
    return session

def getUUID():
    return str(uuid4())


def convert_to_datetime(inp):
    '''converts input string to a valid datetime object'''
    if isinstance(inp, datetime.datetime):
        return inp
    elif isinstance(inp, str):
        ''' "2014-03-05-11-54" '''
        length = len(inp.split('-'))
        if ':' in inp:
            length = length+1
        format = '%Y-%m-%d:%H-%M-%S'
        fmtlen = (length*3) - 1
        fmt = format[:fmtlen]
        return datetime.datetime.strptime(inp, fmt)







class IDMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #__table_args__ = {'mysql_engine': 'InnoDB'}
    #__mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=now)
    modified_on = Column( DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def columnitems(self):
        try:
            return dict([(c, getattr(self, c)) for c in self.columns])
        except AttributeError:
            return self.title

    def __repr__(self):
        return json.dumps(self.columnitems)
