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
import sh

from lxml import etree
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table, \
    Float, Boolean, event, func

from sqlalchemy_utils import PasswordType, aggregated
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from mixin import IDMixin, Base, now, convert_to_datetime
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

project_users = Table('project_users', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('user_id', Integer, ForeignKey('user.id'))
                      )

from db import session
from mako.template import Template


project_reports = Table('project_reports', Base.metadata,
    Column('project_id', Integer, ForeignKey("project.id"),
           primary_key=True),
    Column('report_id', Integer, ForeignKey("report.id"),
           primary_key=True)
)

class Project(IDMixin, Base):

    '''Studio Projects
    '''
    active = Column(Boolean, default=True)
    # 0-active, 1-pending, 2-stopped, 3-finished
    status = Column(Integer, default=0)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text())
    client_id = Column(Integer, ForeignKey("client.id"))
    start = Column(DateTime, nullable=False, default=now)
    end = Column(DateTime, nullable=False)
    client = relationship('Client', backref='projects')
    tasks = relationship(
        'Task', backref='project',
        cascade="all, delete-orphan")
    users = relationship('User', backref='projects', secondary='project_users')
    lead_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    working_days = Column(String(128), default='sat 09:00 - 18:00,')
    lead = relationship('User', backref='leads')
    director = relationship('User', backref='directs')
    is_stereoscopic = Column(Boolean, default=False)
    fps = Column(Float(precision=3), default=24.000)
    tk = relationship('Ticket', backref='project')
    sequences = relationship('Sequence', backref='project')
    tickets = association_proxy('tk', 'Ticket')
    #project_id = Column(Integer, ForeignKey('project.id'))
    rep = relationship("Report", secondary=lambda: project_reports, backref='project')
    reports = association_proxy('rep', 'body') # when we refer to reports, id will be returned.





    @aggregated('tasks', Column(Integer))
    def calculate_number_of_tasks(self):
        return func.sum('1')

    @validates('start')
    def _check_start(self, key, data):
        if data == 'now':
            data = datetime.datetime.utcnow()
        result = convert_to_datetime(data)
        if not self.end:
            # set a default end time for project! 3 months
            self.end = result + datetime.timedelta(days=31 * 3)
        return result

    @validates('end')
    def _check_end(self, key, data):
        result = convert_to_datetime(data)
        #if self.start and data<=self.start:
        ##    result = self.start + datetime.timedelta(days=31*3)
        return result

    @validates('rep')
    def compress_report(self, key, data):
        return data

    #@property
    def plan(self):
        # lets select just one task
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/project.tjp')
        t = Template(filename=templateFile)
        if not self.tasks:
            return
        task = self.tasks[0]
        resources = list()
        tasks = list()
        for each in task.get_tree(session):
            target = each.get('node')
            if target.project == self:
                resources.extend(target.resources)
                tasks.append(target.responsibles)
        
        return tasks
        plan_path = '/tmp/_Fearless_project_%s.tjp' % self.id
        report_path = '/tmp/report.html'
        data = t.render(
            project=self, resources=set(resources), tasks=set(tasks))
        with open(plan_path, 'w') as f:
            f.write(data)

        tj3 = sh.Command('/usr/local/bin/tj3')
        tj = tj3(plan_path, o='/tmp')
        if not tj.stderr:
            report_path = '/tmp/report_%s.html'%self.id
            if os.path.isfile(report_path):
                report = open(report_path)
                root = etree.parse(report)
                main_table = root.xpath('//table')[0]
                tosave = etree.tostring(main_table)
                self.reports.append(tosave)
                session.commit()
            else:
                print 'not available'

            return data
        else:
            print tj.stderr

#def plan_project(mapper, connection, target):
#    target.plan


#event.listen(Project, 'after_insert', plan_project)
