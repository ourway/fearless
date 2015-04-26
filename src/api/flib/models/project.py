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
import hashlib
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, \
    Table, Float, Boolean, event, func

from sqlalchemy_utils import PasswordType, aggregated
import base64
from sqlalchemy.orm import relationship, backref  # for relationships
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.associationproxy import association_proxy
from flib.models.mixin import IDMixin, Base, now, convert_to_datetime, getUUID
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import desc, asc
from flib.utils.defaults import public_upload_folder, public_repository_path, \
    GIT_folder, ASSETS
from flib.models.task import Task
from flib.models.user import User
from flib.models import r
from flib.models.db import session_factory
import ujson as json
from flib.models.helpers import tag_maker, account_maker
from mako.template import Template

project_users = Table('project_users', Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('user_id', Integer, ForeignKey('user.id'))
                      )

project_watchers = Table('project_watchers', Base.metadata,
                         Column('id', Integer, primary_key=True),
                         Column(
                             'project_id', Integer, ForeignKey('project.id')),
                         Column('user_id', Integer, ForeignKey('user.id'))
                         )


project_reports = Table('project_reports', Base.metadata,
                        Column('project_id', Integer, ForeignKey("project.id"),
                               primary_key=True),
                        Column('report_id', Integer, ForeignKey("report.id"),
                               primary_key=True)
                        )


projects_accounts = Table("projects_accounts", Base.metadata,
                          Column('id', Integer, primary_key=True),
                          Column(
                              "project_id", Integer, ForeignKey("project.id"),
                              primary_key=True),
                          Column(
                              "account_id", Integer, ForeignKey("account.id"),
                              primary_key=True)
                          )

projects_tags = Table("projects_tags", Base.metadata,
                      Column('id', Integer, primary_key=True),
                      Column(
                          "project_id", Integer, ForeignKey("project.id"),
                          primary_key=True),
                      Column(
                          "tag_id", Integer, ForeignKey("tag.id"),
                          primary_key=True)
                      )


class Project(IDMixin, Base):

    '''Studio Projects
    '''
    id = Column(
        Integer, primary_key=True)  # over-ride mixin version. because of remote_side
    active = Column(Boolean, default=True)
    # 0-active, 1-pending, 2-stopped, 3-finished
    status = Column(Integer, default=0)
    name = Column(String(64), unique=True, nullable=False)
    last_plan = Column(String(64))  # latest md5 of tjp plan
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
    watchers = relationship(
        'User', backref='watches_projects', secondary='project_watchers')
    lead_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"))
    director_id = Column(Integer, ForeignKey("user.id"))
    lead = relationship('User', backref='leads', foreign_keys=[lead_id])
    director = relationship(
        'User', backref='directs', foreign_keys=[director_id])
    creater = relationship(
        'User', backref='projects_created', foreign_keys=[creator_id])
    working_days = Column(String(128), default='sat 09:00 - 18:00,')
    is_stereoscopic = Column(Boolean, default=False)
    fps = Column(Float(precision=3), default=24.000)
    tk = relationship(
        'Ticket', backref='project', cascade="all, delete, delete-orphan")
    sequences = relationship(
        'Sequence', backref='project', cascade="all, delete, delete-orphan")
    tickets = association_proxy('tk', 'Ticket')
    project_id = Column(Integer, ForeignKey('project.id'))
    rep = relationship(
        "Report", backref='project', cascade="all, delete, delete-orphan")
    # when we refer to reports, id will be returned.
    reports = association_proxy('rep', 'id')
    subproject = relationship("Project", backref='parent', remote_side=[id])
    period = relationship("Date", uselist=False)
    acns = relationship(
        "Account", backref='projects', secondary="projects_accounts")
    accounts = association_proxy('acns', 'name', creator=account_maker)
    tgs = relationship("Tag", backref='projects', secondary="projects_tags")
    tags = association_proxy('tgs', 'name', creator=tag_maker)
    tjp = relationship("Document", uselist=False)
    plan_file = association_proxy('tjp', 'body')

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

        if self.end < self.start:
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


    @validates('name')
    def _check_name(self, key, data):
        return data.replace('\\', '')

    @validates('end')
    def _check_end(self, key, data):
        result = convert_to_datetime(data)
        # if self.start and data<=self.start:
        ##    result = self.start + datetime.timedelta(days=31*3)
        return result

    @validates('rep')
    def compress_report(self, key, data):
        return data

    def tjp_subproject(self, do_plan=True, do_guntt=False, do_resource=False,
                       do_msproject=False, do_profit=False, do_trace=True,
                       do_traceSvg=False, report_width=2000):
        subProjectTemplateFile = os.path.abspath(
            os.path.join( os.path.dirname(__file__), '../templates/subProject.tji'))
        subProjectReportFile = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '../templates/reports.tji'))
        sp = Template(filename=subProjectTemplateFile)
        sr = Template(filename=subProjectReportFile)
        _tasks = []
        #_resources = list()
        for task in self.tasks:
            if not task.parent or (not task.parent and not task.children):
                _tasks.append(task.tjp_task())
            #_resources.extend(task.resources)
        # send tasks in reverse order
        subProjectTasks = sp.render(tasks=_tasks, subproject=self)
        report = sr.render(subproject=self, do_plan=do_plan,
                           do_guntt=do_guntt, do_resource=do_resource,
                           do_msproject=do_msproject, do_profit=do_profit,
                           do_trace=do_trace, do_traceSvg=do_traceSvg,
                           report_width=report_width)
        return {'report': report, 'subProjectTasks': subProjectTasks}

    #@property
    def plan(self, do_plan=True, do_guntt=False, do_resource=False,
             do_msproject=False, do_profit=False, do_trace=True,
             do_traceSvg=False, report_width=1000):
        # lets select just one task
        #puid = getUUID() + '_' + self.uuid
        schedule_path = os.path.join(public_upload_folder,
                                     'Fearless_project_%s.tjp' % self.uuid)
        plan_path = os.path.join(public_upload_folder,
                                 'plan_%s.html' % (self.uuid))
        overall_plan_path = os.path.join(public_upload_folder, 'plan.html')
        overall_gantt_path = os.path.join(public_upload_folder, 'gantt.html')
        overall_resource_path = os.path.join(public_upload_folder, 'resource.html')

        guntt_path = os.path.join(public_upload_folder,
                                  'guntt_%s.html' % (self.uuid))
        resource_path = os.path.join(public_upload_folder,
                                     'resource_%s.html' % (self.uuid))
        msproject_path = os.path.join(public_upload_folder,
                                      'MS-project_%s.xml' % (self.uuid))
        profit_path = os.path.join(public_upload_folder,
                                   'ProfiAndLoss_%s.html' % (self.uuid))
        csv_path = os.path.join(public_upload_folder,
                                'csv_%s.csv' % (self.uuid))
        trace_path = os.path.join(public_upload_folder,
                                  'TraceReport_%s.csv' % (self.uuid))
        traceSvg_path = os.path.join(public_upload_folder,
                                     'TraceReport_%s.html' % (self.uuid))

        if not r.get('fearless_tj3_lock'):
            r.set('fearless_tj3_lock', 'OK')
            # just for highly requested projects
            r.expire('fearless_tj3_lock', 5)
        else:
            return

        if not self.tasks:
            self.reports = []
            return
        templateFile = os.path.abspath(
            os.path.join( os.path.dirname(__file__), '../templates/masterProject.tjp'))
        t = Template(filename=templateFile)
        session = session_factory()
        projects = session.query(Project).order_by(asc(Project.id)).all()
        resources = session.query(User).all()
        subProjectTasks = []
        reports = []
        for p in projects:
            if p.tasks:
                planData = p.tjp_subproject(do_plan=do_plan, do_guntt=do_guntt,
                                            do_resource=do_resource, do_msproject=do_msproject,
                                            do_profit=do_profit, do_trace=do_trace,
                                            do_traceSvg=do_traceSvg, report_width=report_width)
                subProjectTasks.append(planData.get('subProjectTasks'))
                reports.append(planData.get('report'))

        finalplan = t.render(reports=reports, subProjectTasks=subProjectTasks,
                             now=now(), subprojects=projects,
                             resources=resources)

        session.close()

        if self.last_plan == hashlib.md5(finalplan.encode('utf-8', 'ignore')).hexdigest():
            print 'Using cached plan'
            return
        else:
            for i in [schedule_path, plan_path, guntt_path, resource_path,
                      msproject_path, profit_path, csv_path,
                      traceSvg_path]:
                if os.path.isfile(i):
                    os.remove(i)

        #plan_path = '/tmp/Fearless_project.tjp'

        tj3 = sh.Command('../../bin/ruby/bin/tj3')

        with open(schedule_path, 'wb') as f:
            f.write(finalplan.encode('utf-8'))
        try:
            print 'Start Calculating project %s' % self.id
            import time
            s = time.time()
            tj = tj3(schedule_path, '--silent', '--no-color', '--add-trace',
                     o=public_upload_folder, c='1')
            print 'Finished in %s seconds' % round(time.time() - s, 3)
        except Exception, e:
            print e
            # print type(repr(e))
            for i in xrange(3):
                _d = '<br/>'.join(repr(e).split('\\n')[17:]).replace(
                    '\\x1b[31m', '<b>').replace('\\x1b[0m', '</b>').split('\\x1b[35m')
                if len(_d) > 1:
                    self.reports.append(_d[1])
            self.reports = []
            return
        # if not tj.stderr:
        plan, guntt, resource, msproject, profit = None, None, None, None, None
        csvfile, trace, burndown = None, None, None
        
        def change_tm(path):
            if os.path.isfile(path):
                os.system('sed -i s/TaskJuggler/Fearless/ "%s"' % path)
                os.system('sed -i s/taskjuggler.org/fearless.ir/ "%s"' %path)
                os.system('wkhtmltoimage {p} {p}.png'.format(p=path))
                os.system('gzip -f -9 {p}'.format(p=path))
                os.system('gzip -f -9 {p}.png'.format(p=path))

        def saveTable(path):
            '''Read main table from these files'''
            if os.path.isfile(path):
                change_tm(path)

                #report = open(path)
                #root = etree.parse(report)
                # try:
                #    main_table = root.xpath('//table')[0]
                #     root.xpath('//a')[-1].text = 'Fearless'
                #    tosave = etree.tostring(main_table)
                # except lxml.etree.XMLSyntaxError:
                #    pass
                # finally:
                # pass
                #    root.write(path)
                #    pass
                # with open(path, 'wb') as f:
                #    f.write(tosave)

                return path
                # self.reports.append(tosave)

        def getSvg(path):
            '''extract svg element of report'''
            if os.path.isfile(path):
                change_tm(path)
                tosave = None
                #report = open(path)
                # try:
                #    root = etree.parse(report)
                # except lxml.etree.XMLSyntaxError:
                #    return
                # finally:
                #    pass
                # os.remove(path)
                #svg = root.xpath('//svg')[0]
                #tosave = etree.tostring(svg)
                return tosave

        if os.path.isfile(msproject_path):
            os.system('sed -i s/TaskJuggler/Fearless/ "%s"' % msproject_path)
            os.system('sed -i s/taskjuggler.org/fearless.ir/ "%s"' % msproject_path)
            msproject = open(msproject_path, 'rb').read()  # msproject file
        if os.path.isfile(csv_path):
            csvfile = open(csv_path, 'rb').read()  # msproject file
        if os.path.isfile(trace_path):
            trace = open(trace_path, 'rb').read()  # msproject file

        plan = saveTable(plan_path)
        oppl = saveTable(overall_plan_path)
        ogan = saveTable(overall_gantt_path)
        ores = saveTable(overall_resource_path)
        guntt = saveTable(guntt_path)
        resource = saveTable(resource_path)
        profit = saveTable(profit_path)
        burndown = getSvg(traceSvg_path)

        data = {}
        if plan:
            data['plan'] = plan
        if guntt:
            data['guntt'] = guntt
        if resource:
            data['resource'] = resource
        if profit:
            data['profit'] = profit
        if msproject:
            data['msproject'] = msproject
        if csvfile:
            data['csvfile'] = csvfile
        if trace:
            data['trace'] = trace
        if burndown:
            data['burndown'] = burndown
        data = json.dumps(data)

        self.reports = []  # clean old
        self.reports.append(data)
        self.last_plan = hashlib.md5(
            finalplan.encode('utf-8', 'ignore')).hexdigest()
        return data
        # else:
        # return tj.stderr

# def plan_project(mapper, connection, target):
#    target.plan


#event.listen(Project, 'after_insert', plan_project)
