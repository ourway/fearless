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
import datetime
now = datetime.datetime.utcnow()
today = datetime.datetime.strftime(now, '%Y-%m-%d')
from tasks import send_envelope  ## send emails
cc = []
bcc = []


def dailyTasks():
    '''generate an email report of all tasks and send it to users and managers'''
    todays_tasks = session.query(Task).filter(Task.start<now).filter(Task.end>now).all()
    to = ['farsheed.ashouri@gmail.com']
    subject = 'Studio Reports - daily tasks list'
    tasks = ['<li>%s on <span style="color:rgb(113, 62, 0);">%s</span> of <b style="color:darkblue">%s</b> - </li>'\
             %(', '.join(['<span style="color:darkgreen">%s %s</span>'%(u.firstname, u.lastname) for u in i.resources]), i.title, i.project.name) for i in todays_tasks]
    intro = "Good morning, Here is a basic simple (alpha version) report about studio's daily tasks for %s<br/>." % today 
    message = '<hr/>'.join(tasks)
    sent = send_envelope.delay(to, cc, bcc, subject, intro + '<hr/>'+ message + '</hr>')
    return sent
        
        
    




if __name__ == '__main__':
    '''This module should be run directly for crontab'''
    import sys
    if len(sys.argv) < 2:
        print '\tUsage: reports <command>'
        sys.exit()
    command = sys.argv[1]+'()'
    print eval(command)
    sys.exit()

