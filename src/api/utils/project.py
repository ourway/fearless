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
from models import Project, User, Report, Departement, Task, \
    Sequence, Repository, Collection
from AAA import Authorize, getUserInfoFromSession
import falcon
from helpers import get_params
from sqlalchemy import desc
from helpers import commit, jsonify, parse_tjcsv, csv2json
from defaults import home
import datetime
import os
from cStringIO import StringIO


class GetProjectDetails:
    #@Authorize('see_project')
    def on_get(self, req, resp, id):
        project = req.session.query(Project).filter(Project.id==id).first()
        collections = list()
        if project:
            if project.repositories:
                collections = project.repositories[0].collections
            data = {
                'name':project.name.title(), 
                #'tasks':dict.fromkeys(project.tasks, True),
                'id':project.id, 
                'sequences':[{'number':i.number, 'name':i.name, 'code':i.code} for i in project.sequences],
                'description':project.description,
                'start':project.start,
                'end':project.end,
                'effort_left':project.effort_left,
                'effort_done':project.effort_done,
                'duration':project.duration,
                'effort':project.effort,
                'uuid':project.uuid,
                'complete':project.complete,
                'watchers':[{'firstname':i.firstname, 'lastname':i.lastname, 'fullname':i.fullname, 'id':i.id} for i in project.watchers], 
                #'tasks':[{'title':i.title, 'id':i.id} for i in project.tasks],
                'collections':[{'name':i.name.title(), 'id':i.id, 'path':i.path, 
                                'repository':i.repository.name.title(),
                                'repository_path':i.repository.path} for i in collections if not i.parent]}
            if project.lead_id:
                data['leader'] = {'fullname':project.lead.fullname, 'id':project.lead.id}
            if project.director:
                data['director'] = {'fullname':project.director.fullname, 'id':project.director.id}


            resp.body = data
        else:
            resp.status = falcon.HTTP_404




class ListProjects:
    def on_get(self, req, resp):
        user = getUserInfoFromSession(req, resp)

        if user.get('id') != 1:
            project = req.session.query(Project).order_by(desc(Project.modified_on)).all()
        else:
            project = req.session.query(Project).order_by(desc(Project.modified_on)).all()

        resp.body = project


class AddProject:
    def on_put(self, req, resp):
        user = getUserInfoFromSession(req, resp)
        projectData = get_params(req.stream, flat=False)
        start, end, name, lead_id, description = None, None, None, None, None
        if projectData.get('start'):
            start = str(projectData.get('start'))
        if projectData.get('end'):
            end = str(projectData.get('end'))
        if projectData.get('name'):
            name = str(projectData.get('name'))
        if projectData.get('description'):
            description = str(projectData.get('description'))
        if projectData.get('lead_id'):
            lead_id = int(projectData.get('lead_id'))

        if start and end and name and lead_id: 
            new = Project(start=start, name=name, end=end, lead_id=lead_id)
            if description:
                new.description = description
            repoName = name
            newRepoFolder = os.path.join(home, '.fearlessrepo', repoName)
            if not os.path.isdir(newRepoFolder):
                os.makedirs(newRepoFolder)
            new_repository = req.session.query(Repository).filter(Repository.name == repoName).first()
            if not new_repository:
                new_repository = Repository(name=repoName, path= newRepoFolder)
            
            chars_section = Collection(name='Characters', path='chars')
            props_section = Collection(name='Props', path='props')
            sets_section = Collection(name='Sets', path='sets')
            sequences_section = Collection(name='Sequences', path='sequences')
            editorial_section = Collection(name='Editorial', path='editorial')

            new_repository.collections.append(chars_section)
            new_repository.collections.append(props_section)
            new_repository.collections.append(sets_section)
            new_repository.collections.append(sequences_section)
            new_repository.collections.append(editorial_section)


            new.repositories.append(new_repository)
            req.session.add(new)
            resp.body = falcon.HTTP_202
            resp.body = {'message':'OK'}


        #project = session.query(Project).filter(Project.lead_id==user.get('id')).all()
        #resp.body = project


class GetProjectLatestReport:
    #@Authorize('see_project')
    def on_get(self, req, resp, id):
        project = req.session.query(Project).filter(Project.id==id).first()
        if not project:
            resp.status = falcon.HTTP_404
            return
        data = project.plan()  ## first let it plan
        if not data:
            reports = project.reports
            if reports:
                repid = reports[-1]
                report = req.session.query(Report).filter_by(id=repid).first()
                if report:
                    data = report.body
        if data:
            datajson = json.loads(data)
            csvfile = StringIO()
            csvdata = datajson.get('csvfile')
            if csvdata:
                csvfile.write(csvdata.encode('utf-8'))
            try:
                csvjsondata = parse_tjcsv(csvfile)
            except IndexError:
                return
            csvfile = StringIO()
            tracecsv = datajson.get('trace')
            if tracecsv:
                csvfile.write(tracecsv.encode('utf-8'))
            try:
                traceJsonData = csv2json(csvfile)
            except IndexError:
                return
            
            if not csvjsondata:
                resp.body = {}
                return
            for each in csvjsondata:
                d =  csvjsondata[each]
                typ = d.get('type')
                if typ == 'task':
                    taskid = int(d.get('taskid'))
                    target = req.session.query(Task).filter(Task.id==taskid).first()
                elif typ == 'project':
                    projectid = int(d.get('projectid'))
                    target = req.session.query(Project).filter(Project.id==projectid).first()
                if target: ## donble check
                    start = d.get('start')
                    end = d.get('end')
                    duration = d.get('duration')
                    criticalness = d.get('criticalness')
                    complete = d.get('completion')
                    if complete:
                        complete = complete[:-1]
                    effort = d.get('effort')
                    effort_left = d.get('effort left')
                    effort_done = d.get('effort done')
                    gauge = d.get('gauge')

                    if typ == 'task':
                        target.start = start
                        target.computed_start = start
                        target.computed_end = end
                        target.end = end
                    target.complete = complete
                    target.criticalness = criticalness
                    target.computed_complete = complete
                    target.gauge = gauge
                    target.effort = effort
                    target.effort_left = effort_left
                    target.effort_done = effort_done
                    target.duration = duration

            data = datajson
            data['json'] = csvjsondata
            data['trace'] = traceJsonData
            resp.body = data

        else:
            resp.status = falcon.HTTP_201
            message = None
            data = {'guntt':message, 'plan':message, 'resource':message, 
                    'profitAndLoss':message, 'msproject':message, 'csv':message }
            resp.body = data


class UpdateProject:
    def on_post(self, req, resp, projId):
        user = getUserInfoFromSession(req, resp)
        data = get_params(req.stream, flat=False)
        project = req.session.query(Project).filter(Project.id==int(projId)).first()
        if project:
            project.start = data.get('start')
            project.name = data.get('name')
            project.end = data.get('end')
            project.description= data.get('description')
            project.lead_id = int(data.get('leader').get('id'))
            project.watchers = []
            if data.get('watchers'):
                for eachWatcherId in data.get('watchers'):
                    _id = int(eachWatcherId.get('id'))
                    watcher = req.session.query(User).filter(User.id == _id).first()
                    project.watchers.append(watcher)


            resp.body = {'message':'OK'}
        else:
            resp.status = falcon.HTTP_404




class AddTask:
    def on_put(self, req, resp, projId):
        user = getUserInfoFromSession(req, resp)
        taskData = get_params(req.stream, flat=False)
        resources, depends, manager, effort = list(), list(), 0, 0
        title = taskData.get('title')
        if taskData.get('effort'): effort = int(taskData.get('effort'))
        start = taskData.get('start')
        end = taskData.get('end')
        priority = taskData.get('priority')
        project = req.session.query(Project).filter(Project.id==int(projId)).first()
        if not start:
           start = project.start
        else:
            start = str(start)

        newTask = Task(title=title, effort=effort, project=project, start=start)
        newTask.priority = priority
        if end:
            newTask.end = str(end)

        if taskData.get('resources'): resources = [int(i.get('id')) for i in taskData.get('resources')]
        if taskData.get('depends'): depends = [int(i.get('id')) for i in taskData.get('depends')]
        if taskData.get('manager'): manager = int(taskData.get('manager').get('id'))
        for i in resources:
            resource = req.session.query(User).filter(User.id==i).first()
            if resource: newTask.resources.append(resource)
        if manager:
            manager = req.session.query(User).filter(User.id==manager).first()
            if manager: newTask.responsibles.append(manager)
        for i in depends:
            depend = req.session.query(Task).filter(Task.id==i).first()
            if depend: newTask.depends.append(depend)
        #depend = session.query(Task).filter(Task.id==depends).first()
        #newTask.depends.append(depend)
        req.session.add(newTask)
        resp.body = {'message':'OK'}


class ListTasks:
    def on_get(self, req, resp, projId):
        user = getUserInfoFromSession(req, resp)
        project = req.session.query(Project).filter(Project.id==projId).first()
        if project:
            resp.body = [{
                    'start':i.start,
                    'end':i.end,
                    'title':i.title,
                    'id':i.id,
                    'effort':i.effort,
                    'complete':i.complete,
                    'dependent_of':[{'title':j.title, 'id':j.id} for j in i.dependent_of],
                    'depends':[{'title':g.title, 'id':g.id} for g in i.depends],
                    'resources':[{'id':k.id, 'lastname':k.lastname} for k in i.resources]
            
            } for i in project.tasks]


class GetTask:
    def on_get(self, req, resp, taskId):
        task = req.session.query(Task).filter(Task.id==taskId).first()
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
                     'project':{'id':task.project.id, 'name':task.project.name, 'start':task.project.start, 'end':task.project.end}
                     }

class UpdateTask:
    def on_post(self, req,resp, taskId):
        user = getUserInfoFromSession(req, resp)
        resources, depends, responsibles, effort , alternative_resources = list(), list(), list(), 0, list()
        taskData = get_params(req.stream, flat=False)
        if taskData.get('resources'): resources = [int(i.get('id')) for i in taskData.get('resources')]
        if taskData.get('updatedResponsibles'): responsibles = taskData.get('updatedResponsibles')
        if taskData.get('depends'): depends = [int(i.get('id')) for i in taskData.get('depends')]
        if taskData.get('updatedAlternativeResources'): alternative_resources = taskData.get('updatedAlternativeResources')
        if taskData.get('updatedWatchers'): watchers = taskData.get('updatedWatchers')

        complete = int(taskData.get('complete'))
        effort = int(taskData.get('effort'))
        start = str(taskData.get('start'))
        end = str(taskData.get('end'))
        title = taskData.get('title')
        priority = taskData.get('priority')
        _id = int(taskData.get('id'))
        priority = int(taskData.get('priority'))
        target = req.session.query(Task).filter(Task.id==_id).first()
        if target:
            target.title = title
            target.start = start
            target.priority = priority
            target.end = end
            target.effort = effort
            if effort:
                target.complete = complete
            if resources:
                target.resources = []
            for i in resources:
                resource = req.session.query(User).filter(User.id==i).first()
                if not resource in target.project.users:
                    target.project.users.append(resource)
                if resource: target.resources.append(resource)
            if depends:
                target.depends = []
            for i in depends:
                depend = req.session.query(Task).filter(Task.id==i).first()
                if depend: target.depends.append(depend)
            
            resp.body = {'message':'Task Updated'}
        else:
            resp.status = falcon.HTTP_404
            resp.body = {'message':'Task Not Found'}

class DeleteTask:
    def on_delete(self, req, resp, taskId):
        user = getUserInfoFromSession(req, resp)
        target = req.session.query(Task).filter(Task.id==taskId).first()
        if target:
            req.session.delete(target)
            resp.status = falcon.HTTP_202

        else:
            resp.status = falcon.HTTP_404

class UserTasksCard:
    def on_get(self, req, resp, date):
        user = getUserInfoFromSession(req, resp)
        uid = int(user.get('id'))
        now = datetime.datetime.utcnow
        today = now().strftime('%Y-%m-%d') 
        tomorrow = (now() + datetime.timedelta(hours=24)).strftime('%Y-%m-%d')
        if date == 'today':
            '''These are tasks that started today and not finished yet'''
            data = req.session.query(Task).filter(Task.resources.any(id=uid))\
                .filter(Task.start<=now())\
                .filter(Task.complete<100).filter(Task.end>now()).all()
        elif date == 'before':
            '''These are tasks that should have been ended before nut not completed yet'''
            data = req.session.query(Task).filter(Task.resources.any(id=uid))\
                .filter(Task.end<=now()).filter(Task.complete<100).all()


        resp.body = [
            {
                'title':i.title,
                'id':i.id,
                'project':{
                    'id':i.project.id,
                    'name':i.project.name,
                }
            }
            for i in data]






