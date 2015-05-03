#!../../pyenv/bin/python
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

import sys
import os
current_path = os.path.dirname(__file__)
from guess_language import guessLanguage as gl
pta = os.path.abspath(os.path.join(current_path, '../../'))
# print pta
sys.path.append(pta)

from guess_language import guessLanguage as lg
from flib.models import Project, Review, Task, User, Report, r, fdb
from flib.models.db import session_factory
from sqlalchemy import or_, and_
import arrow
from datetime import date, timedelta
from flib.tasks import send_envelope  # send emails
from mako.template import Template
import os
from collections import defaultdict
from sqlalchemy import desc, asc
from calverter import Calverter
cal = Calverter()
import misaka


templates_folder = os.path.join(os.path.dirname(__file__), '../templates')


cc = []
bcc = []

'''Dates'''
now = arrow.utcnow()
year, month, day = now.year, now.month, now.day
jd = cal.gregorian_to_jd(year, month, day)
jtoday = '/'.join(map(str, cal.jd_to_jalali(jd)))
today = now.format('YYYY-MM-DD')
_yesterday = date.today() - timedelta(1)
yesterday = _yesterday.strftime('%Y-%m-%d')
_tomorrow = date.today() + timedelta(1)
tomorrow = _tomorrow.strftime('%Y-%m-%d')
print '*' * 80
print '\tReporting on %s' % today
print '*' * 80

################################################################
session = session_factory()

'''On going tasks:  Tasks that started and are not finished'''


projects = session.query(Project).all()

for i in projects:
    i.plan()

ongoing_tasks = session.query(Task).filter(or_(Task.gauge == 'on schedule', Task.gauge == 'ahead of schedule'))\
    .order_by(desc(Task.complete)).all()
'''Behind schedule tasks:  Tasks that are not finished on time and are not completed yet'''
behind_tasks = session.query(Task).filter_by(gauge='behind schedule')\
    .order_by(asc(Task.end)).all()


#################################################################


def getTemplate(name):
    t = os.path.join(templates_folder, name)
    return Template(filename=t)


def dailyTasksReportForClients():
    '''generate an email report of all tasks and send it to users and managers'''
    message =  getTemplate('email_daily_tasks_for_clients.html')\
        .render(ongoing_tasks=ongoing_tasks, behind_tasks=behind_tasks, today=today,
                jtoday=jtoday, arrow=arrow, recipient='product owner', responsibility='managing')

    # print message
    # return
    #to = ['hamid2177@gmail.com', 'alishahdad1353@yahoo.com']
    to = ['hamid2177@gmail.com']
    #to = ['farsheed.ashouri@gmail.com']
    subject = 'Studio Reports - Daily Tasks - %s' % jtoday
    #intro = "Good morning, Here is a basic simple (alpha version) report about studio's daily tasks for %s<br/>." % today
    #message = '<hr/>'.join(tasks)
    sent = send_envelope.delay(to, cc, bcc, subject, message)
    return sent


def dailyTasksReportForProjectLeads():
    '''Daily tasks report for project leaders'''
    managerOngoingTasks = defaultdict(list)
    managerBehindTasks = defaultdict(list)
    for task in ongoing_tasks:
        managerOngoingTasks[task.project.lead].append(task)
    for task in behind_tasks:
        managerBehindTasks[task.project.lead].append(task)
    target_users = list(
        set(managerBehindTasks.keys() + managerOngoingTasks.keys()))
    for target in target_users:
        target_behind_tasks = managerBehindTasks[target]
        target_ongoing_tasks = managerOngoingTasks[target]
        to = [target.email]
        #to = ['hamid2177@gmail.com']
        #to = [target.email]
        subject = 'Studio Reports - Daily Tasks for your projects - %s' % jtoday
        message =  getTemplate('email_daily_tasks_for_clients.html')\
            .render(ongoing_tasks=target_ongoing_tasks, behind_tasks=target_behind_tasks,
                    today=today, jtoday=jtoday, arrow=arrow, recipient=target.firstname,
                    responsibility='leading')

        sent = send_envelope.delay(to, cc, bcc, subject, message)
        print 'Report sent to %s' % target.email
    return True


def dailyTaskCardForResources():
    '''Daily tasks card for reources'''
    resourceOngoingTasks = defaultdict(list)
    resourceBehindTasks = defaultdict(list)
    for task in ongoing_tasks:
        for resource in task.resources:
            resourceOngoingTasks[resource].append(task)
    for task in behind_tasks:
        for resource in task.resources:
            resourceBehindTasks[resource].append(task)
    target_users = list(
        set(resourceBehindTasks.keys() + resourceOngoingTasks.keys()))
    for target in target_users:
        target_behind_tasks = resourceBehindTasks[target]
        target_ongoing_tasks = resourceOngoingTasks[target]
        to = [target.email]
        #to = ['hamid2177@gmail.com']
        #to = ['farsheed.ashouri@gmail.com']
        subject = 'Studio Reports - Task card - %s' % jtoday
        message =  getTemplate('email_daily_tasks_for_clients.html')\
            .render(ongoing_tasks=target_ongoing_tasks, behind_tasks=target_behind_tasks,
                    today=today, jtoday=jtoday, arrow=arrow, recipient=target.firstname,
                    responsibility='contributing to')

        sent = send_envelope.delay(to, cc, bcc, subject, message)
        print 'Report sent to %s' % target.email
    return True


def dailyUserReportsToClients():
    reports = session.query(Report).filter(Report.user).\
        filter(Report.created_on.between(yesterday, tomorrow))\
        .order_by(desc(Report.created_on)).all()

    if not reports:
        print '\tnot any report available'
        return
    result = []
    for i in reports:
        data = {
            'reporter': {'id': i.user[0].id, 'firstname': i.user[0].firstname,
                         'lastname': i.user[0].lastname},
            'body': misaka.html(i.body),
            'datetime': arrow.get(i.created_on),
            'prettytime': arrow.get(i.created_on).humanize(),
            'tgs': i.tgs,
            'lang':lg(i.body)
        }
        result.append(data)

    tasks = []
    message =  getTemplate('email_daily_user_reports_for_clients.html')\
        .render(today=today, tasks=tasks, jtoday=jtoday, arrow=arrow, reports=result,
                responsibility='leading')
    subject = 'Studio Daily Reports - %s' % jtoday
    #emails =  ['hamid2177@gmail.com', 'alishahdad1353@yahoo.com']
    emails =  ['hamid2177@gmail.com']
    #emails =  ['farsheed.ashouri@gmail.com']
    sent = send_envelope.delay(emails, cc, bcc, subject, message)
    print 'Report sent to %s' % emails


    return


def dailyTaskReviewsToClients():
    revs = session.query(Review).filter(Review.created_on>yesterday)\
        .order_by(desc(Review.created_on)).all()

    return


if __name__ == '__main__':
    '''This module should be run directly for crontab'''
    import sys
    if len(sys.argv) < 2:
        print '\tUsage: reports <command>'
        print '\t------------------'
        print '\tAvailable commands are:'
        print '\t\t dailyTasksReportForClients'
        print '\t\t dailyTasksReportForProjectLeads'
        print '\t\t dailyTaskCardForResources'
        print '\t\t dailyUserReportsToClients'
        print '\t\t dailyTaskReviewsToClients'
        print '\t------------------'
        sys.exit()
    command = sys.argv[1] + '()'
    print eval(command)
    session.close()
    sys.exit()
