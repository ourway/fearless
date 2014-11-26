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
import datetime


class GetProjectDetails:
    #@Authorize('see_project')
    def on_get(self, req, resp, id):
        project = session.query(Project).filter(Project.id==id).first()
        if project:
            resp.body = {'name':project.name, 'tasks':dict.fromkeys(project.tasks, True),
                     'id':project.id, 'leader':project.lead.fullname}


class ListProjects:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req)

        if user.get('id') != 1:
            project = session.query(Project).order_by(desc(Project.modified_on)).all()
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
        if project:
            project.plan() ## first let it plan
            if project.reports:
                resp.body = {'report':project.reports[-1], 'resource':project.reports[-2]}


class AddTask:
    @falcon.after(commit)
    def on_put(self, req, resp, projId):
        user = getUserInfoFromSession(req)
        taskData = get_params(req.stream, flat=False)
        resources, depends, manager, effort = list(), list(), 0, 0
        title = taskData.get('title')
        if taskData.get('effort'): effort = int(taskData.get('effort'))
        start = taskData.get('start')
        #print responsible_id
        newTask = Task(title=title, effort=effort)
        project = session.query(Project).filter(Project.id==int(projId)).first()
        if not start:
            newTask.start = project.start
        else:
            newTask.start = start
            
        newTask.project = project
        if taskData.get('resource'): resources = taskData.get('resource').split(',')
        if taskData.get('depends'): depends = taskData.get('depends').split(',')
        if taskData.get('manager'): manager = int(taskData.get('manager'))
        for i in resources:
            resource = session.query(User).filter(User.id==int(i)).first()
            newTask.resources.append(resource)
        for i in depends:
            depend = session.query(Task).filter(Task.id==int(i)).first()
            newTask.depends.append(depend)
        #depend = session.query(Task).filter(Task.id==depends).first()
        #newTask.depends.append(depend)
        session.add(newTask)


class ListTasks:
    def on_get(self, req, resp, projId):
        user = getUserInfoFromSession(req)
        project = session.query(Project).filter(Project.id==projId).first()
        if project:
            resp.body = [{'title':i.title, 'id':i.id} for i in project.tasks]


class GetTask:
    def on_get(self, req, resp, taskId):
        task = session.query(Task).filter(Task.id==taskId).first()
        resp.body = {'title':task.title, 'id':task.id, 'start':task.start, 
                     'end':task.end, 'effort':task.effort, 
                     'depends':[{'name':i.title, 'id':i.id} for i in task.depends],
                     'dependent_of':[{'name':i.title, 'id':i.id} for i in task.dependent_of],
                     'resources':[{'fullname':i.fullname, 'id':i.id} for i in task.resources],
                     'watchers':[{'fullname':i.fullname, 'id':i.id} for i in task.watchers],
                     'alternative_resources':[{'fullname':i.fullname, 'id':i.id} for i in task.alternative_resources],
                     'responsibles':[{'fullname':i.fullname, 'id':i.id} for i in task.responsibles],
                     'priority':task.priority,
                     'complete':task.complete,
                     'duration':task.duration,
                     'project_start':task.project.start,
                     'project_end':task.project.end
                     }

class UpdateTask:
    @falcon.after(commit)
    def on_post(self, req,resp, taskId):
        user = getUserInfoFromSession(req)
        taskData = get_params(req.stream, flat=False)
        resources = taskData.get('resources')
        responsibles = taskData.get('responsibles')
        alternative_resources = taskData.get('alternative_resources')
        watchers = taskData.get('watchers')
        depends = taskData.get('depends')
        complete = int(taskData.get('complete'))
        effort = int(taskData.get('effort'))
        start = str(taskData.get('start'))
        end = str(taskData.get('end'))
        title = taskData.get('title')
        _id = int(taskData.get('id'))
        priority = taskData.get('priority')
        target = session.query(Task).filter(Task.id==_id).first()
        if target:
            target.title = title
            target.start = start
            target.end = end
            target.effort = effort
            target.complete = complete
            resp.body = {'message':'Task Updated'}
        else:
            resp.status = falcon.HTTP_404
            resp.body = {'message':'Task Not Found'}






