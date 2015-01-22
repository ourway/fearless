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
import datetime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event

from utils.general import setup_logger
from utils.helpers import dumps
from uuid import uuid4  # for random guid generation
import base64

now = datetime.datetime.utcnow

Base = declarative_base()
logger = setup_logger('model', 'model.log')
db_files_path = os.path.join(os.path.dirname(__file__), '../database/files')
if not os.path.isdir(db_files_path):
    os.makedirs(db_files_path)


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')


def convert_to_datetime(inp):
    '''converts input string to a valid datetime object'''
    if inp == 'None':
        return
    try:
        unixtime = int(inp)
        return datetime.datetime.fromtimestamp(unixtime)
    except (ValueError, TypeError):
        pass

    if isinstance(inp, datetime.datetime):
        return inp

    elif isinstance(inp, (float, int)):  # unix timestamp
        return datetime.datetime.fromtimestamp(inp)

    elif isinstance(inp, (str, unicode)):
        ''' "2014-03-05-11-54" '''
        length = len(inp.split('-'))
        if ':' in inp:
            length = length + 1
        format = '%Y-%m-%d:%H-%M-%S'

        fmtlen = (length * 3) - 1
        fmt = format[:fmtlen]
        if 'T' in inp:
            ''' 2015-01-08T00:00:00.000Z '''
            inp = inp.split('T')[0]
            fmt = '%Y-%m-%d'
        #inp = '-'.join(map(str, map( int, inp.split(';')[0].split('-'))) )
        # print inp, fmt
        return datetime.datetime.strptime(inp, fmt)


class IDMixin(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #__table_args__ = {'mysql_engine': 'InnoDB'}
    #__mapper_args__= {'always_refresh': True}
    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), default=getUUID)
    created_on = Column(DateTime, default=now)
    modified_on = Column(DateTime, default=now, onupdate=now)

    @property
    def columns(self):
        data = [c.name for c in self.__table__.columns]
        return data

    @property
    def columnitems(self):
        try:
            data = [(c, getattr(self, c)) for c in self.columns]
            return dict([i for i in data
                         if isinstance(i[1], (str, unicode, datetime.datetime, long, int, float, bool))])
        except AttributeError, e:
            print e
            return self.title

    def __repr__(self):
        return dumps(self.columnitems)
