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

from models import session, Task, User, Report, r, fdb
import arrow
from tasks import send_envelope  ## send emails
from mako.template import Template
import os
from sqlalchemy import desc, asc
from calverter import Calverter
cal = Calverter()


templates_folder = os.path.join(os.path.dirname(__file__), 'templates')


cc = []
bcc = []

'''Dates'''
now = arrow.utcnow()
year, month, day = now.year, now.month, now.day
jd = cal.gregorian_to_jd(year,month,day)
jtoday = '/'.join(map(str, cal.jd_to_jalali(jd)))
today = now.format('YYYY-MM-DD')



'''On going tasks:  Tasks that started and are not finished'''
ongoing_tasks = session.query(Task).filter(Task.start<now.date())\
            .filter(Task.end>now.date()).order_by(desc(Task.complete)).all()
'''Behind schedule tasks:  Tasks that are not finished on time and are not completed yet'''
behind_tasks = session.query(Task).filter(Task.end<now.date())\
            .filter(Task.complete<100).order_by(asc(Task.end)).all()


def getTemplate(name):
    t = os.path.join(templates_folder, name)
    return Template(filename=t)

def dailyTasksReportForClients():
    '''generate an email report of all tasks and send it to users and managers'''
    message =  getTemplate('email_daily_tasks_for_clients.html')\
        .render(ongoing_tasks=ongoing_tasks, behind_tasks=behind_tasks, today=today, jtoday=jtoday, arrow=arrow)
    #to = ['hamid2177@gmail.com']
    to = ['farsheed.ashouri@gmail.com']
    subject = 'Studio Reports - Daily Tasks - %s' % jtoday
    #intro = "Good morning, Here is a basic simple (alpha version) report about studio's daily tasks for %s<br/>." % today 
    #message = '<hr/>'.join(tasks)
    sent = send_envelope.delay(to, cc, bcc, subject, message)
    return sent
        
        
    




if __name__ == '__main__':
    '''This module should be run directly for crontab'''
    import sys
    if len(sys.argv) < 2:
        print '\tUsage: reports <command>'
        print '\t------------------'
        print '\tAvailable commands are:'
        print '\t\tdailyTasksReportForClients'
        print '\t------------------'
        sys.exit()
    command = sys.argv[1]+'()'
    print eval(command)
    sys.exit()

