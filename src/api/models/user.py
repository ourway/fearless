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

import re
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event
from . import Group, now
from db import Session
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base, getUUID, logger, convert_to_datetime
import datetime

users_groups = Table('users_groups', Base.metadata,
                     Column('id', Integer, primary_key=True),
                     Column('user_id', Integer, ForeignKey('user.id')),
                     Column('group_id', Integer, ForeignKey('group.id'))
                     )




user_vacations = Table('user_vacations', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('date_id', Integer, ForeignKey("date.id"),
           primary_key=True)
)

user_leaves = Table('user_leaves', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('date_id', Integer, ForeignKey("date.id"),
           primary_key=True)
)

user_shifts = Table('user_shifts', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('date_id', Integer, ForeignKey("date.id"),
           primary_key=True)
)


user_offdays = Table('user_offdays', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('date_id', Integer, ForeignKey("date.id"),
           primary_key=True)
)


user_reports = Table('user_reports', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('report_id', Integer, ForeignKey("report.id"),
           primary_key=True)
)


user_accounts = Table('user_accounts', Base.metadata,
    Column('user_id', Integer, ForeignKey("user.id"),
           primary_key=True),
    Column('account_id', Integer, ForeignKey("account.id"),
           primary_key=True)
)

class User(IDMixin, Base):

    '''Main users group
    '''
    id = Column( Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    email = Column(String(64), unique=True, nullable=False)
    paypal = Column(String(64), unique=True)
    password = Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    avatar = Column(Text())
    token = Column(String(64), default=getUUID, unique=True)
    firstname = Column(String(64), nullable=True)
    job = Column(String(64))
    persian_firstname = Column(String(64))
    alias = Column(String(64), nullable=True)
    lastname = Column(String(64), nullable=True)
    persian_lastname = Column(String(64))
    hasFrequentPayment = Column(Boolean(), default=True)
    payment_type = Column(String(64), nullable=True, default='monthly') ## , manually. ..
    lastLogIn = Column(DateTime)
    age = Column(Integer)
    efficiency = Column(Float(precision=3), default=1.0)
    effectiveness = Column(Float(precision=3), default=1.0)
    cell = Column(String(16))
    address = Column(String(512))
    budget_account = Column(Integer, default=0) 
    bank = Column(String(64), default='Paarsian')
    bank_account_number = Column(String(64))
    debit_card_number = Column(String(64), default='0000-0000-0000-0000')
    daily_working_hours = Column(Integer, default=8)
    weeklymax = Column(Integer, default=44)
    monthly_working_hours = Column(Integer, default=192)
    monthly_present_hours = Column(Float(precision=3), default=0)
    off_days = Column(String(32), default='fri')
    latest_session_id = Column(String(64))
    active = Column(Boolean, default=False)
    fulltime = Column(Boolean, default=True)
    is_client = Column(Boolean, default=False)
    rate = Column(Float(precision=3), default=0)
    monthly_salary = Column(Float(precision=3), default=0)
    extra_payment = Column(Float(precision=3), default=0)
    retention = Column(Float(precision=3), default=10)
    payroll_tax = Column(Float(precision=3), default=3)
    insurance_deductions = Column(Float(precision=3), default=7.8)
    reps = relationship("Report", secondary=lambda: user_reports, backref='user')
    agreements = relationship("Document", backref='agreement_of')
    payment_invoices = relationship("Document", backref='invoice_of')
    chargeset = relationship("Account", backref='users', secondary="user_accounts")
    agreement_period = relationship("Date", uselist=False)
    reports = association_proxy('reps', 'id') # when we refer to reports, id will be returned.
    grps = relationship('Group', backref='users', secondary='users_groups')
    groups = association_proxy('grps', 'name')
    tgs = relationship("Tag", backref='users')
    tags = association_proxy('tgs', 'name')

    @validates('email')
    def _validate_email(self, key, data):
        if re.match(r'[^@]+@[^@]+\.[^@]+', data):
            if not self.alias:
                self.alias = data.split('@')[0].replace('.', '_')
            #self.groups.append(self.alias)
            return data

    @validates('firstname')
    def capitalize_firstname(self, key, data):
        return data.title()

    @validates('lastname')
    def capitalize_firstname(self, key, data):
        return data.title()

    @validates('agreement_start')
    def check_agreement_start(self, key, data):
        data = convert_to_datetime(data)
        if not data:
            data = now()
        return data

    @validates('agreement_end')
    def check_agreement_end(self, key, data):
        data = convert_to_datetime(data)
        if not data:
            data = now()
        return data


    @hybrid_property
    def fullname(self):
        return (self.firstname or '<>') + " " + (self.lastname or '<>')

    @hybrid_property
    def finished_tasks(self):
        'Not Implemented'
        pass

    @hybrid_property
    def open_tasks(self):
        'Not Implemented'
        pass
    # group =
    #reports = Set("Report")
    #groups = Set("Group")

def AfterUserCreationFuncs(mapper, connection, target):
    '''Some operations after getting ID'''
    logger.info('New user added|{t.id}|{t.email}'.format(t=target))
    session=Session()  ## old session is closed...
    user = session.query(User).filter(User.id==target.id).first()
    if target.id == 1: ## first user is admin!
        adminGroup = session.query(Group).filter(Group.name=='admin').first()
        user.grps.append(adminGroup)
    else:
        usersGroup = session.query(Group).filter(Group.name=='users').first()
        if not usersGroup in user.grps:
            user.grps.append(usersGroup)
    session.commit()


event.listen(User, 'after_insert', AfterUserCreationFuncs)
