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
from AAA import Authorize, getUserInfoFromSession
import falcon
from helpers import get_params
from sqlalchemy import desc
from utils.helpers import commit, jsonify


class GetProjectDetails:
    #@Authorize('see_project')
    def on_get(self, req, resp, id):
        project = session.query(Project).filter(Project.id==id).first()
        resp.body = {'name':project.name, 'tasks':dict.fromkeys(project.tasks, True),
                     'id':project.id, 'leader':project.lead.fullname}


class ListProjects:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req)
        if user.get('id') != 1:
            project = session.query(Project).filter(Project.lead_id==user.get('id')).order_by(desc(Project.modified_on)).all()
        else:
            project = session.query(Project).order_by(desc(Project.modified_on)).all()


        resp.body = project


class AddProject:
    'NOT WORKING YET'
    def on_put(self, req, resp):
        user = getUserInfoFromSession(req)
        projectData = get_params(req.stream, flat=False)
        if Project(start=projectData.get('start'),
                   name = projectData.get('name'),
                   end=projectData.get('end'), lead_id=projectData.get('lead_id')):
            resp.body = falcon.HTTP_202
            resp.body = {'message':'OK'}


        #project = session.query(Project).filter(Project.lead_id==user.get('id')).all()
        #resp.body = project


class GetProjectLatestReport:
    #@Authorize('see_project')
    def on_get(self, req, resp, id):
        project = session.query(Project).filter(Project.id==id).first()
        print project.plan() ## first let it plan
        if project.reports:
            resp.body = {'report':project.reports[-1]}


class AddTask:
    @falcon.after(commit)
    def on_put(self, req, resp, projId):
        user = getUserInfoFromSession(req)
        taskData = get_params(req.stream, flat=False)
        title = taskData.get('title')
        effort = int(taskData.get('effort'))
        responsible_id = int(taskData.get('responsible'))
        #print responsible_id
        responsible = session.query(User).filter(User.id==responsible_id).first()
        print responsible
        newTask = Task(title=title, effort=effort)
        session.add(newTask)
        newTask.responsibles.append(responsible)
        newTask.project_id = int(projId)



