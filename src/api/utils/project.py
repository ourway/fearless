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

import ujson as json
from models import Project, User, Report, Departement, Task, session
from AAA import Authorize
import falcon


class GetProjectDetails:
    @Authorize('see_project')
    def on_get(self, req, resp, id):
        project = session.query(Project).filter(Project.id==id).first()
        resp.body = {'name':project.name, 'tasks':dict.fromkeys(project.tasks, True),
                     'id':project.id, 'leader':project.lead.fullname}


class GetProjectLatestReport:
    @Authorize('see_project')
    def on_get(self, req, resp, id):
        project = session.query(Project).filter(Project.id==id).first()
        project.plan ## first let it plan
        if project.reports:
            resp.body = {'report':project.reports[-1]}


