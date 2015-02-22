#!../../pyenv/bin/python

import os
from mako.template import Template
import json as json
from models import User, Task, Expert, Project
from models.db import session_factory
from uuid import uuid4  # for random guid generation
import base64
from collections import OrderedDict


def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')


def sort_by_order(a):
    return a[1].get('order')


def render_process(session, t, project_id, prefix, parent=None, last_order=0):
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
    raw_root = templ.render()
    plan = json.loads(raw_root)
    outputs = []
    found_tasks = False
    # print plan
    old_t = session.query(Task).filter_by(
        title=prefix + (parent or t)).filter_by(project_id=project_id).scalar()
    newt = old_t
    if not newt:
        newt = Task(
            title= (prefix+(parent or t)).decode('utf-8'), project_id=project_id, priority=600 - last_order)
        session.add(newt)




    if plan.get('processes'):
        processes = OrderedDict(
            sorted(plan.get('processes').items(), key=sort_by_order))

        list_of_order_numbers = [
            processes.get(i).get('order') for i in processes.keys()]
        remainings = []
        multies = []
        plan['processes'] = processes
        for process in processes.keys():
            depends = []
            _id = getUUID()
            plan['processes'][process]['uuid'] = _id

            #po = last_order + 1
            po = processes.keys().index(process)
            old_task = session.query(Task).filter_by(
                title=prefix + process).filter_by(project_id=project_id).scalar()
            new = old_task
            if not new:
                new = Task(
                    title=prefix + process, project_id=project_id, priority=600 - po, uuid=_id)
                session.add(new)
            else:
                new.uuid = _id
            new.parent.append(newt)


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
            last_order = max(po, last_order-1)
            last_order += 1
            deps = plan['processes'][process].get('depends_on')
            if po:
                previous = processes.keys()[po-1]
                pdb = session.query(Task).filter_by(title=prefix+previous).filter_by(project_id=project_id).scalar()
                new.depends.append(pdb)
                print '%s depnds on %s' % (process, previous)



            process_plan = render_process(
                session, plan['processes'][process]['template'], project_id, prefix, process, last_order)

            if process_plan:
                outputs = [_this]
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
        for task in tasks.keys():
            if not task:
                continue
            _id = getUUID()
            plan['tasks'][task]['uuid'] = _id
            #to = last_order+1
            to = tasks.keys().index(task)
            #to = int(plan['tasks'][task]['order'])
            depends = outputs
            nt = session.query(Task).filter_by(
                title=prefix + task).filter_by(project_id=project_id).scalar()
            if not nt:
                nt = Task(title=prefix + task, project_id=project_id, uuid=_id, priority=to)
                session.add(nt)
            else:
                nt.uuid = _id

            nt.parent.append(newt)

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
                
            deps = plan['tasks'][task].get('depends_on') or []


            '''
            if to and parent:
                #previous = processes.keys()[po-1]
                pdb = session.query(Task).filter_by(title=prefix+parent).filter_by(project_id=project_id).scalar()
                if pdb and not nt in pdb.depends:
                    #print process, '|::::::::>', previous
                    nt.depends.append(pdb)

            if deps:
                for i in deps:
                    dep_title = prefix+i.get('name')
                    dep = session.query(Task).filter_by(title=dep_title).filter_by(project_id=project_id).scalar()
                    assert dep != nt
                    nt.depends.append(dep)
            if parent:
                print '%s{ %s }' % (parent, task)
                #print prefix+parent
                tdb = session.query(Task).filter_by(title=prefix+parent).filter_by(project_id=project_id).scalar()
                if tdb and not tdb in nt.depends:
                    tdb.children.append(nt)
            '''

            if to:
                previous = tasks.keys()[to-1]
                tdb = session.query(Task).filter_by(title=prefix+previous).filter_by(project_id=project_id).scalar()
                if tdb and not nt in tdb.depends:
                    nt.depends.append(tdb)

            last_order = max(to, last_order-1)
            last_order += 1
            

            if plan['tasks'][task].get('template'):
                process_task = render_task(plan['tasks'][task]['template'], session,
                                           project_id, task, prefix, plan['tasks'][task].get('template'), order=600 - to, depends=deps)
                if process_task:
                    found_tasks = True
                    outputs = [_this]
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


def render_task(t, session, project_id, parent, prefix, title, order, depends):
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
        if Sresources:
            parent_task = session.query(Task).filter_by(title=prefix+parent).scalar()

            theTask = session.query(Task).filter_by(
                title=prefix+title+'_task').filter_by(project_id=project_id).scalar()
            if not theTask:
                theTask = Task(
                    title=prefix + title + '_task', project_id=project_id, uuid=_id, effort=effort, priority=order)
            else:
                theTask.uuid = _id
            if parent_task:
                assert parent_task!=theTask
                #if not parent_task in theTask.depends:
                    #theTask.depends.append(parent_task)
                theTask.parent = [parent_task]
            '''
            if depends:
                for i in depends:
                    dep_title = prefix+i.get('name')
                    dep = session.query(Task).filter_by(title=dep_title).filter_by(project_id=project_id).scalar()
                    assert dep != theTask
                    if not dep in theTask.parent:
                        theTask.depends.append(dep)
            '''


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
    character_preproduction_template = "Art_character_preproduction"
    session = session_factory()
    plan = render_process(
        session, character_preproduction_template, 3, 'sepehr_')
    session.commit()
    session.close()
    #flat = flatten(plan)
