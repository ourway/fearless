#!../../pyenv/bin/python

import os
from mako.template import Template
import json as json
from models import User, Task, Expert, Project
from models.db import Session
from uuid import uuid4  # for random guid generation
import base64
from collections import OrderedDict
import datetime


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')


def sort_by_order(a):
    return a[1].get('order')


def render_process(session, t, project_id, prefix):
    ''' 
        Renders a process template
        @t: mako template
        @responsible: integer,
        @watchers: list of integers,
        @order: integer,
        @desciption: string

    '''
    fn = 'templates/TPlans/processes/' + t + '.json'
    structure = {'processes': {}, 'tasks': {}}
    if not os.path.isfile(fn):
        with open(fn, 'wb') as f:
            f.write(json.dumps(structure, sort_keys=True, indent=4))
    templ = Template(filename=fn)  # create a mako template
    raw_root = templ.render()
    plan = json.loads(raw_root)
    outputs = []
    last_order = 0
    found_tasks = False
    # print plan

    if plan.get('processes'):
        processes = OrderedDict(
            sorted(plan.get('processes').items(), key=sort_by_order))
        list_of_order_numbers = [
            processes.get(i).get('order') for i in processes.keys()]
        remainings = []
        multies = []
        plan['processes'] = processes
        for process in processes:

            depends = []
            _id = getUUID()
            plan['processes'][process]['uuid'] = _id

            po = int(plan['processes'][process]['order'])
            old_task = session.query(Task).filter_by(
                title=prefix + process).filter_by(project_id=project_id).first()
            if not old_task:
                new = Task(
                    title=prefix + process, project_id=project_id, priority=600 - po, uuid=_id)
                session.add(new)
            else:
                old_task.uuid = _id

            _this = {'name': process, 'uuid': _id, 'order': po}
            if list_of_order_numbers.count(po) > 1:
                multies.append(_this)
                remainings = outputs
                if po > last_order and outputs:
                    plan['processes'][process]['depends_on'] = outputs
                elif po == last_order and remainings:
                    plan['processes'][process]['depends_on'] = remainings

            else:
                if multies:
                    outputs = multies
                    multies = []
                if outputs:
                    plan['processes'][process]['depends_on'] = outputs
                outputs = [_this]
            last_order = max(po, last_order)

            process_plan = render_process(
                session, plan['processes'][process]['template'], project_id, prefix)

            if process_plan:
                subprocesses = process_plan.get('processes')
                subtasks = process_plan.get('tasks')
                if subprocesses:
                    plan['processes'][process]['processes'] = subprocesses
                elif plan['processes'][process].get('processes'):
                    del(plan['processes'][process]['processes'])

                if subtasks:
                    plan['processes'][process]['tasks'] = subtasks
                elif plan['processes'][process].get('tasks'):
                    del(plan['processes'][process]['tasks'])

            else:
                # print "plan for " + plan['processes'][process]['template'] +
                # " not available"
                del(plan['processes'][process])

    if plan.get('tasks'):
        tasks = OrderedDict(
            sorted(plan.get('tasks').items(), key=sort_by_order))
        list_of_order_numbers = [
            tasks.get(i).get('order') for i in tasks.keys()]
        remainings = []
        multies = []
        plan['tasks'] = tasks
        for task in tasks:
            if not task:
                continue
            _id = getUUID()
            depends = outputs
            nt = session.query(Task).filter_by(
                title=prefix + task).filter_by(project_id=project_id).first()
            if not nt:
                nt = Task(title=prefix + task, project_id=project_id, uuid=_id)
                session.add(nt)
            else:
                nt.uuid = _id
            plan['tasks'][task]['uuid'] = _id

            to = int(plan['tasks'][task]['order'])
            _this = {'name': task, 'uuid': _id, 'order': to}
            if list_of_order_numbers.count(to) > 1:
                multies.append(_this)
                remainings = outputs
                if to > last_order and outputs:
                    plan['tasks'][task]['depends_on'] = outputs
                elif to == last_order and remainings:
                    plan['tasks'][task]['depends_on'] = remainings

            else:
                if multies:
                    outputs = multies
                    multies = []
                plan['tasks'][task]['depends_on'] = outputs
                
                outputs = [_this]
            deps = plan['tasks'][task].get('depends_on')
            for i in deps:
                dep_title = prefix+i.get('name')
                dep = session.query(Task).filter_by(title=dep_title).filter_by(project_id=project_id).first()
                assert dep != nt
                nt.depends.append(dep)

            last_order = max(to, last_order)
            

            if plan['tasks'][task].get('template'):
                process_task = render_task(plan['tasks'][task]['template'], session,
                                           project_id, _id, prefix, plan['tasks'][task].get('template'))
                if process_task:
                    found_tasks = True
                    plan['tasks'][task]['plan'] = process_task
            else:
                del(plan['tasks'][task])
                print('\tWarning: task "%s -> %s" has not any template!' %
                      (t, task))

    # if not found_tasks:
    #    return {}

    with open('templates/TPlans/plan.json', 'wb') as f:
        f.write(json.dumps(plan))
    return plan


def render_task(t, session, project_id, parent, prefix, title):
    '''lets see what will happen'''
    fn = 'templates/TPlans/tasks/' + t + '.json'
    structure = {'tags': [], 'min_effort': 0, 'max_effort': 2,
                 'resource_expertize': {}, 'outputs': {}}
    if not os.path.isfile(fn):
        with open(fn, 'wb') as f:
            f.write(json.dumps(structure, sort_keys=True, indent=4))
    templ = Template(filename=fn)  # create a mako template
    raw_process = templ.render()
    _id = getUUID()
    task = json.loads(raw_process)
    task['parent'] = parent
    task['title'] = title
    task['uuid'] = _id
    _expert = task.get('resource_expertize')
    min_effort = task.get('min_effort')
    max_effort = task.get('max_effort')
    task['effort'] = effort = (max_effort + min_effort) / 2.0
    if _expert.keys():
        Rate = _expert[_expert.keys()[0]]
        minRate = Rate['minimum_rate']
        _expert = _expert.keys()[0]
    resources = list()
    eDb = session.query(Expert).filter_by(name=_expert).first()
    if eDb:
        resources = eDb.users
    else:
        raise ValueError(
            'Expertise: "%s" that is specified is not found in database.' % _expert)
    if resources:
        Sresources = [{'name': i.fullname, 'id': i.id, 'uuid': i.uuid, 'effectiveness': i.effectiveness}
                      for i in resources if i.effectiveness >= minRate]
        if Sresources:
            parent_task = session.query(Task).filter_by(uuid=parent).first()
            theTask = session.query(Task).filter_by(
                title=prefix+title+'_task').filter_by(project_id=project_id).first()
            if not theTask:
                theTask = Task(
                    title=prefix + title + '_task', project_id=project_id, uuid=_id, effort=effort)
            else:
                theTask.uuid = _id
            if parent_task:
                assert parent_task!=theTask
                if not theTask in parent_task.depends:
                    theTask.depends.append(parent_task)
                else:
                    print parent_task.title, theTask.title
            theTask.resources = [
                i for i in resources if i.effectiveness >= minRate]
            session.add(theTask)
            task['resources'] = Sresources
        else:
            raise ValueError(
                'Cant find any reources for expertise "%s"' % _expert)
    return task


def flatten(plan):
    flat = {"tasks": []}
    if plan.get('tasks'):
        for i in plan.get('tasks'):
            task = plan['tasks'][i]
            flat["tasks"].append(task)
    prs = plan.get('processes')
    target = prs
    while True:
        if not target:
            break
        for i in target:
            process = target.get(i)
            if process.get('tasks'):
                # if target.get('tasks'):
                flat['tasks'].append(process.get('tasks'))
        target = target.get('processes')

    with open('templates/TPlans/flat.json', 'wb') as f:
        f.write(json.dumps(flat))
    return flat


if __name__ == '__main__':
    character_preproduction_template = "character_preproduction"
    session = Session
    plan = render_process(
        session, character_preproduction_template, 11, 'merida_')
    session.commit()
    session.close()
    flat = flatten(plan)
