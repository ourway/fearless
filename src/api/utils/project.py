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
from utils.helpers import commit, jsonify, parse_tjcsv
import datetime
from cStringIO import StringIO


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
                try:
                    csvfile = StringIO()
                    csvdata = project.reports[-1]
                    csvfile.write(csvdata)
                    jsondata = parse_tjcsv(csvfile)
                    for each in jsondata:
                        d =  jsondata[each]
                        typ = d.get('type')
                        if typ == 'task':
                            taskid = int(d.get('taskid'))
                            target = session.query(Task).filter(Task.id==taskid).first()
                        elif typ == 'project':
                            projectid = int(d.get('projectid'))
                            target = session.query(Project).filter(project.id==projectid).first()
                        if target: ## donble check
                            start = d.get('start')
                            end = d.get('end')
                            duration = d.get('duration')
                            complete = d.get('completion')
                            if complete:
                                complete = complete[:-1]
                            effort = d.get('effort')
                            effort_left = d.get('effort_left')
                            effort_done = d.get('effort_done')

                            if typ == 'task':
                                target.start = start
                                target.end = end
                            target.complete = complete
                            target.effort = effort
                            target.effort_left = effort_left
                            target.effort_done = effort_done
                            target.duration = duration

                    data = {'guntt':project.reports[-2], 'plan':project.reports[-3], 'resource':project.reports[-4], 
                            'profitAndLoss':project.reports[-6], 'msproject': project.reports[-5], 'json': jsondata }
                except IndexError:
                    message = "We're busy planning your project. Please wait a bit or reload."
                    data = {'guntt':message, 'plan':message, 'resource':message, 
                            'profitAndLoss':message, 'msproject':message, 'csv':message }

                resp.body = data
            else:
                message = "There is no report available. Try adding some tasks."
                data = {'guntt':message, 'plan':message, 'resource':message, 
                        'profitAndLoss':message, 'msproject':message, 'csv':message }




class AddTask:
    @falcon.after(commit)
    def on_put(self, req, resp, projId):
        user = getUserInfoFromSession(req)
        taskData = get_params(req.stream, flat=False)
        resources, depends, manager, effort = list(), list(), 0, 0
        title = taskData.get('title')
        if taskData.get('effort'): effort = int(taskData.get('effort'))
        start = taskData.get('start')
        end = taskData.get('end')
        #print responsible_id
        project = session.query(Project).filter(Project.id==int(projId)).first()
        if not start:
           start = project.start
        else:
            start = str(start)

        newTask = Task(title=title, effort=effort, project=project, start=start)
        if end:
            newTask.end = str(end)

        if taskData.get('resources'): resources = map(int, taskData.get('resources'))
        if taskData.get('depends'): depends = map(int, taskData.get('depends'))
        if taskData.get('manager'): manager = int(taskData.get('manager'))
        for i in resources:
            resource = session.query(User).filter(User.id==i).first()
            if resource: newTask.resources.append(resource)
        if manager:
            manager = session.query(User).filter(User.id==manager).first()
            if manager: newTask.responsibles.append(manager)
        for i in depends:
            depend = session.query(Task).filter(Task.id==i).first()
            if depend: newTask.depends.append(depend)
        #depend = session.query(Task).filter(Task.id==depends).first()
        #newTask.depends.append(depend)
        session.add(newTask)


class ListTasks:
    def on_get(self, req, resp, projId):
        user = getUserInfoFromSession(req)
        project = session.query(Project).filter(Project.id==projId).first()
        if project:
            resp.body = [{'start':i.start, 'title':i.title, 'id':i.id, 'dependent_of':[{'title':j.title} for j in i.dependent_of]} for i in project.tasks]


class GetTask:
    def on_get(self, req, resp, taskId):
        task = session.query(Task).filter(Task.id==taskId).first()
        resp.body = {'title':task.title, 'id':task.id, 'start':task.start, 
                     'end':task.end, 'effort':task.effort, 
                     'depends':[{'title':i.title, 'id':i.id} for i in task.depends],
                     'dependent_of':[{'title':i.title, 'id':i.id} for i in task.dependent_of],
                     'resources':[{'fullname':i.fullname, 'id':i.id} for i in task.resources],
                     'watchers':[{'fullname':i.fullname, 'id':i.id} for i in task.watchers],
                     'alternative_resources':[{'fullname':i.fullname, 'id':i.id} for i in task.alternative_resources],
                     'responsibles':[{'fullname':i.fullname, 'id':i.id} for i in task.responsibles],
                     'priority':task.priority,
                     'complete':task.complete,
                     'uuid':task.uuid,
                     'duration':task.duration,
                     'project_start':task.project.start,
                     'project_end':task.project.end
                     }

class UpdateTask:
    @falcon.after(commit)
    def on_post(self, req,resp, taskId):
        user = getUserInfoFromSession(req)
        resources, depends, responsibles, effort , alternative_resources = list(), list(), list(), 0, list()
        taskData = get_params(req.stream, flat=False)
        print taskData
        if taskData.get('updatedResources'): resources = taskData.get('updatedResources')
        if taskData.get('updatedResponsibles'): responsibles = taskData.get('updatedResponsibles')
        if taskData.get('updatedDepends'): depends = taskData.get('updatedDepends')
        if taskData.get('updatedAlternativeResources'): alternative_resources = taskData.get('updatedAlternativeResources')
        if taskData.get('updatedWatchers'): watchers = taskData.get('updatedWatchers')

        complete = int(taskData.get('complete'))
        effort = int(taskData.get('effort'))
        start = str(taskData.get('start'))
        end = str(taskData.get('end'))
        title = taskData.get('title')
        _id = int(taskData.get('id'))
        priority = int(taskData.get('priority'))
        target = session.query(Task).filter(Task.id==_id).first()
        if target:
            target.title = title
            target.start = start
            target.end = end
            target.effort = effort
            if effort:
                target.complete = complete
            if resources:
                target.resources = []
            for i in resources:
                resource = session.query(User).filter(User.id==int(i)).first()
                if not resource in target.project.users:
                    target.project.users.append(resource)
                if resource: target.resources.append(resource)
            if depends:
                target.depends = []
            for i in depends:
                depend = session.query(Task).filter(Task.id==int(i)).first()
                if depend: target.depends.append(depend)
            
            resp.body = {'message':'Task Updated'}
        else:
            resp.status = falcon.HTTP_404
            resp.body = {'message':'Task Not Found'}

class DeleteTask:
    @falcon.after(commit)
    def on_delete(self, req, resp, taskId):
        user = getUserInfoFromSession(req)
        target = session.query(Task).filter(Task.id==taskId).first()
        if target:
            session.delete(target)
            resp.status = falcon.HTTP_202

        else:
            resp.status = falcon.HTTP_404






