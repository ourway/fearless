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
from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base, getUUID, logger, convert_to_datetime
from utils.helpers import expertizer, tag_maker, group_maker,\
    departement_maker, account_maker
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


users_accounts = Table('users_accounts', Base.metadata,
                      Column('user_id', Integer, ForeignKey("user.id"),
                             primary_key=True),
                      Column('account_id', Integer, ForeignKey("account.id"),
                             primary_key=True)
                      )

users_expertise = Table('users_expertise', Base.metadata,
                      Column('user_id', Integer, ForeignKey("user.id"),
                             primary_key=True),
                      Column('expert_id', Integer, ForeignKey("expert.id"),
                             primary_key=True)
                      )

users_tags = Table('users_tags', Base.metadata,
                      Column('user_id', Integer, ForeignKey("user.id"),
                             primary_key=True),
                      Column('tag_id', Integer, ForeignKey("tag.id"),
                             primary_key=True)
                      )

users_departements = Table('users_departements', Base.metadata,
                      Column('user_id', Integer, ForeignKey("user.id"),
                             primary_key=True),
                      Column('departement_id', Integer, ForeignKey("departement.id"),
                             primary_key=True)
                      )



class User(IDMixin, Base):

    '''Main users group
    '''
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
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
    # , manually. ..
    payment_type = Column(String(64), nullable=True, default='monthly')
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
    reps = relationship(
        "Report", secondary=lambda: user_reports, backref='user')
    agreements = relationship("Document", backref='agreement_of')
    payment_invoices = relationship("Document", backref='invoice_of')

    agreement_period = relationship("Date", uselist=False)
    # when we refer to reports, id will be returned.
    reports = association_proxy('reps', 'id')
    exps = relationship('Expert', backref='users', secondary='users_expertise')
    expertise = association_proxy('exps', 'name', creator=expertizer)
    groups = association_proxy('grps', 'name')
    grps = relationship('Group', backref='users', secondary='users_groups')
    acns = relationship('Account', backref='users', secondary='users_accounts')
    accounts = association_proxy('acns', 'name', creator=account_maker)
    groups = association_proxy('grps', 'name', creator=group_maker)
    dps = relationship("Departement", backref='users', secondary="users_departements")
    departements = association_proxy('dps', 'name', creator=departement_maker)
    tgs = relationship("Tag", backref='users', secondary="users_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)




    @validates('email')
    def _validate_email(self, key, data):
        if not 'users' in self.groups:
            self.groups.append('users')
        if not 'admin' in self.groups:
            pass
        if re.match(r'[^@]+@[^@]+\.[^@]+', data):
            if not self.alias:
                self.alias = data.split('@')[0].replace('.', '_')
            # self.groups.append(self.alias)
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


    @staticmethod
    def AfterUserCreationFuncs(mapper, connection, target):
        '''Some operations after getting ID'''
        pass

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'after_insert', cls.AfterUserCreationFuncs)
