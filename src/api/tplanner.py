#!../../pyenv/bin/python

import os
from mako.template import Template
import json as json
from models import User, Task, Expert, Project
from models.db import session_factory
from uuid import uuid4  # for random guid generation
import base64
from collections import OrderedDict, defaultdict


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')


def sort_by_order(a):
    return a[1].get('order')


def render_process(session, t, project_id, prefix, parent=None, last_order=0, depends=[]):
    ''' 
        Renders a process template
        @t: mako template
        @responsible: integer,
        @watchers: list of integers,
        @order: integer,
        @desciption: string

    '''
    session.commit()
    fn = 'templates/TPlans/processes/' + t + '.json'
    structure = {'processes': {}, 'tasks': {}}
    if not os.path.isfile(fn):
        with open(fn, 'wb') as f:
            f.write(json.dumps(structure, sort_keys=True, indent=4))
    templ = Template(filename=fn)  # create a mako template
    print 'processing %s' % prefix+t
    raw_root = templ.render()
    plan = json.loads(raw_root)
    if plan.get('active') and plan.get('active') == True:
        print 'bypassing inactive process/task "%s"' % t
        return
    outputs = []
    found_tasks = False
    # print plan
    old_t = session.query(Task).filter_by(
        title=(prefix+(parent or t)).decode('utf-8')).filter_by(project_id=project_id).scalar()
    newt = old_t
    if not newt:
        newt = Task(
            title=(prefix+(parent or t)).decode('utf-8'), project_id=project_id, priority=600-last_order)
        session.add(newt)
    if depends and all(depends):   ## I am using a custom force depend list for external dependency injection
        print t, depends[0].title
        newt.depends = depends
    #    callerTask = session.query(Task).filter_by(title=prefix+parent).one()
    #    newt.parent = [callerTask]


    everything = list()

    ## lets get everything and add it to a list
    ALL = defaultdict(list)
    for METHOD in ['tasks', 'processes']:
        contents = plan.get(METHOD)
        if contents:
            ALL[METHOD] += contents.items()
            everything += contents.items()

    ## now we need to sort it based on its order number
    everything =  sorted(everything, key=sort_by_order)
    ## ok, now we have all items without knowing their METHOD
    ## let's iterate and create some tasks.  the main challenge is to 
    ## find a tasks method for now.. We may need another search on plan.

    for process in everything:
        title, info = process
        template = info['template']  ## an info should have a template
        title = prefix+title
        processTask = session.query(Task).filter_by(title=title).scalar()
        if not processTask:
            processTask = Task(title=title, project_id=project_id)
            session.add(processTask)
        process[1]['db'] = processTask
        processTask.parent = [newt]  ## a parent is a list in architecture
                                     ## each process depends on upper creator
        previous = [p for p in everything if p[1]['order']==int(info['order'])-1]
        for each in previous:                        ## for every process that in lower order
            processTask.depends.append(each[1]['db'])    ## we are going to add that process to
                                                     ## dependency list.
        ## now lets also find sub processes. its recursive

        
        if process in ALL['processes']:
            render_process(session, template, project_id, prefix, parent=process[0], last_order=0)
        else:
            render_task(template, session,
                    project_id, process[0], prefix, process[0], order=600-info['order'])


        
    return newt


def render_task(t, session, project_id, parent, prefix, title, order):
    '''lets see what will happen'''
    session.commit()
    fn = 'templates/TPlans/tasks/' + t + '.json'
    structure = {'tags': [], 'min_effort': 0, 'max_effort': 2,
                 'resource_expertize': {"NULL":{"minimum_rate":0.75}}, 'outputs': {}}
    if not os.path.isfile(fn):
        with open(fn, 'wb') as f:
            f.write(json.dumps(structure, sort_keys=True, indent=4))
    templ = Template(filename=fn)  # create a mako template
    raw_process = templ.render()
    task = json.loads(raw_process)
    task['parent'] = parent
    task['title'] = title
    _expert = task.get('resource_expertize')
    min_effort = task.get('min_effort')
    max_effort = task.get('max_effort')
    task['effort'] = effort = (max_effort + min_effort) / 2.0
    if _expert.keys():
        Rate = _expert[_expert.keys()[0]]
        minRate = Rate['minimum_rate']
        _expert = _expert.keys()[0]
    else:
        raise ValueError('Expertize is empty in task: %s' % t)
    resources = list()
    eDb = session.query(Expert).filter_by(name=_expert).scalar()
    if eDb:
        resources = eDb.users
        if not resources:
            raise ValueError(
                        'Resource not found for: "%s" that is specified in "%s" is not found in database.'\
                            % (_expert, t))
    else:
        raise ValueError(
            'Expertise: "%s" that is specified in %s is not found in database.' % (_expert, t))
    if resources:
        Sresources = [{'name': i.fullname, 'id': i.id, 'uuid': i.uuid, 'effectiveness': i.effectiveness}
                      for i in resources if i.effectiveness >= minRate]
        if Sresources:  ## we need resources to allocation 
            theTask = session.query(Task).filter_by(
                title=prefix+title+'_task').filter_by(project_id=project_id).scalar()

            if not theTask:
                theTask = Task(
                    title=prefix + title + '_task', project_id=project_id, effort=effort, priority=order)

            if parent:
                parent_task = session.query(Task).filter_by(title=prefix+parent).one()
                theTask.parent = [parent_task]

            theTask.resources = [
                i for i in resources if i.effectiveness >= minRate]
            session.add(theTask)
        else:
            raise ValueError(
                'Cant find any reources for expertise "%s"' % _expert)
    return theTask




if __name__ == '__main__':
    character_preproduction_template = "Art_character_preproduction"
    PROJ = 3
    session = session_factory()
    prodb = session.query(Project).filter_by(id=PROJ).one()  ## must be present

    ### for test only
    prodb.tasks = []
    session.commit()

    render_process( session, character_preproduction_template, PROJ, 'Sepehr_')  ## depends must be a list
    render_process( session, character_preproduction_template, PROJ, 'Tiger_')  ## depends must be a list
    session.commit()

    prodb.plan(do_plan=True, do_guntt=True, do_resource=True, report_width=1700)
    session.commit()

    session.close()
    #flat = flatten(plan)
