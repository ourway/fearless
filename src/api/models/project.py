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
import lxml
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
from sqlalchemy import desc, asc
from .task import Task
from .user import User
from . import r
from utils.helpers import dumps

project_users = Table('project_users', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('user_id', Integer, ForeignKey('user.id'))
                      )

project_watchers = Table('project_watchers', Base.metadata,
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
    id = Column( Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    active = Column(Boolean, default=True)
    # 0-active, 1-pending, 2-stopped, 3-finished
    status = Column(Integer, default=0)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text())
    client_id = Column(Integer, ForeignKey("client.id"))
    start = Column(DateTime, nullable=False, default=now)
    end = Column(DateTime, nullable=False)
    duration = Column(Float(precision=3), default=0)
    effort = Column(Float(precision=3), nullable=False, default=0)
    effort_left = Column(Float(precision=3), default=0)
    effort_done = Column(Float(precision=3), default=0)
    length = Column(Float(precision=3), default=0)
    complete = Column(Integer, default=0)
    client = relationship('Client', backref='projects')
    tasks = relationship(
        'Task', backref='project',
        cascade="all, delete, delete-orphan")
    users = relationship('User', backref='projects', secondary='project_users')
    watchers = relationship('User', backref='watches_projects', secondary='project_watchers')
    lead_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"))
    director_id = Column(Integer, ForeignKey("user.id"))
    lead = relationship('User', backref='leads', foreign_keys=[lead_id])
    director = relationship('User', backref='directs', foreign_keys=[director_id])
    creater = relationship('User', backref='projects_created', foreign_keys=[creator_id])
    working_days = Column(String(128), default='sat 09:00 - 18:00,')
    is_stereoscopic = Column(Boolean, default=False)
    fps = Column(Float(precision=3), default=24.000)
    tk = relationship('Ticket', backref='project', cascade="all, delete, delete-orphan")
    sequences = relationship('Sequence', backref='project', cascade="all, delete, delete-orphan")
    tickets = association_proxy('tk', 'Ticket')
    project_id = Column(Integer, ForeignKey('project.id'))
    rep = relationship("Report",backref='project', cascade="all, delete, delete-orphan")
    reports = association_proxy('rep', 'id') # when we refer to reports, id will be returned.
    subproject = relationship("Project", backref='parent', remote_side=[id])
    period = relationship("Date", uselist=False)
    account = relationship("Account", backref='projects')


    @aggregated('tasks', Column(Integer))
    def calculate_number_of_tasks(self):
        return func.sum('1')

    @validates('start')
    def _check_start(self, key, data):
        if data == 'now':
            data = now()
        result = convert_to_datetime(data)
        if not self.end:
            # set a default end time for project! 3 months
            self.end = result + datetime.timedelta(days=31 * 3)

        return result


    @validates('tasks')
    def recalculate_end(self, key, data):
        if not self.start and self.end:
            return data

        if self.end<self.start:
            self.end = self.start + datetime.timedelta(days=31 * 3)

        if not data.start:
            data.start = self.start

        for task in self.tasks:
            if task.start < self.start:
                task.start = self.start
            if task.end < task.start:
                task.end = max(task.start, task.end)
        if self.end:
            task_ends = [i.end for i in self.tasks]
            if task_ends and max(task_ends) > self.end:
                self.end = max(task_ends)
            if data.end and data.end > self.end:
                self.end = data.end
        return data



    @validates('end')
    def _check_end(self, key, data):
        result = convert_to_datetime(data)
        #if self.start and data<=self.start:
        ##    result = self.start + datetime.timedelta(days=31*3)
        return result

    @validates('rep')
    def compress_report(self, key, data):
        return data

    def tjp_subproject(self):
        subProjectTemplateFile = os.path.join(
            os.path.dirname(__file__), '../templates/subProject.tji')
        subProjectReportFile = os.path.join(
            os.path.dirname(__file__), '../templates/reports.tji')
        sp = Template(filename=subProjectTemplateFile)
        sr = Template(filename=subProjectReportFile)
        _tasks = []
        #_resources = list()
        for task in self.tasks:
            _tasks.append(task.tjp_task())
            #_resources.extend(task.resources)
        subProjectTasks = sp.render(tasks=_tasks, subproject=self)  ## send tasks in reverse order
        report = sr.render(subproject=self)
        return {'report':report, 'subProjectTasks':subProjectTasks}





    #@property
    def plan(self):
        # lets select just one task
        if not r.get('fearless_tj3_lock'):
            r.set('fearless_tj3_lock', 'OK')
            r.expire('fearless_tj3_lock', 30)
        else:
            return
        templateFile = os.path.join(
            os.path.dirname(__file__), '../templates/masterProject.tjp')
        t = Template(filename=templateFile)
        projects = session.query(Project).order_by(asc(Project.id)).all()
        resources = session.query(User).all()
        subProjectTasks = []
        reports = []
        for p in projects:
            if p.tasks:
                planData = p.tjp_subproject()
                subProjectTasks.append(planData.get('subProjectTasks'))
                reports.append(planData.get('report'))

        finalplan = t.render(reports=reports, subProjectTasks=subProjectTasks, 
                       now=now(), subprojects = projects, resources=resources
                       )

        #plan_path = '/tmp/Fearless_project.tjp'
        plan_path = '/home/farsheed/Desktop/Fearless_project_%s.tjp' % self.uuid
        with open(plan_path, 'wb') as f:
            f.write(finalplan.encode('utf-8'))

        tj3 = sh.Command('/usr/local/bin/tj3')
        try:
            print 'Start Calculating project %s' % self.id
            import time
            s = time.time()
            tj = tj3(plan_path, '--silent', '--no-color', '--add-trace', o='/tmp', c='1')
            print 'Finished in %s seconds' % round(time.time()-s, 3)
        except Exception,e:
            #print type(repr(e))
            for i in xrange(3):
                _d = '<br/>'.join(repr(e).split('\\n')[17:]).replace('\\x1b[31m', '<b>').replace('\\x1b[0m','</b>').split('\\x1b[35m')
                if len(_d)>1:
                    self.reports.append(_d[1])
            session.commit()
            return
        #if not tj.stderr:
        plan, guntt, resource, msproject, profit, csvfile, trace, burndown = None, None, None, None, None, None, None, None
        plan_path = '/tmp/plan_%s.html' % (self.uuid)
        guntt_path = '/tmp/guntt_%s.html' % (self.uuid)
        resource_path = '/tmp/resource_%s.html' % (self.uuid)
        msproject_path = '/tmp/MS-project_%s.xml' % (self.uuid)
        profit_path = '/tmp/ProfiAndLoss_%s.html' % (self.uuid)
        csv_path = '/tmp/csv_%s.csv' % (self.uuid)
        trace_path = '/tmp/TraceReport_%s.csv' % (self.uuid)
        traceSvg_path = '/tmp/TraceReport_%s.html' % (self.uuid)

        def saveTable(path):
            '''Read main table from these files'''
            if os.path.isfile(path):
                report = open(path)
                root = etree.parse(report)
                try:
                    main_table = root.xpath('//table')[0]
                except lxml.etree.XMLSyntaxError:
                    return

                tosave = etree.tostring(main_table)
                return tosave
                #self.reports.append(tosave)
        def getSvg(path):
            '''extract svg element of report'''
            if os.path.isfile(path):
                report = open(path)
                try:
                    root = etree.parse(report)
                except lxml.etree.XMLSyntaxError:
                    return
                svg = root.xpath('//svg')[0]
                tosave = etree.tostring(svg)
                return tosave

        if os.path.isfile(msproject_path):
            msproject = open(msproject_path, 'rb').read()  # msproject file
        if os.path.isfile(csv_path):
            csvfile = open(csv_path, 'rb').read()  # msproject file
        if os.path.isfile(trace_path):
            trace = open(trace_path, 'rb').read()  # msproject file

        plan = saveTable(plan_path)
        guntt = saveTable(guntt_path)
        resource = saveTable(resource_path)
        profit = saveTable(profit_path)
        burndown = getSvg(traceSvg_path)

        data = {}
        if plan: data['plan'] = plan
        if guntt: data['guntt'] = guntt
        if resource: data['resource'] = resource
        if profit: data['profit'] = profit
        if msproject: data['msproject'] = msproject
        if csvfile: data['csvfile'] = csvfile
        if trace: data['trace'] = trace
        if burndown: data['burndown'] = burndown
        data = dumps(data)
        self.reports.append(data)
        session.commit()
        return data 
        #else:
        #return tj.stderr

#def plan_project(mapper, connection, target):
#    target.plan


#event.listen(Project, 'after_insert', plan_project)
