#!../../../../pyenv/bin/python
from mako.template import Template
import json as json
from uuid import uuid4  # for random guid generation
import base64
from collections import OrderedDict
import datetime
class Task:
    effort = 0
    duration = 0
    depends = []
    uuid = None
    resources = []
    start = None
    end = None
    milestone = None

def getUUID():
    data = base64.encodestring(uuid4().get_bytes()).strip()[:-2]
    return data.replace('/', '-')

def sort_by_order(a):
    return a[1].get('order')

def render_process(t):
    ''' 
        Renders a process template
        @t: mako template
        @responsible: integer,
        @watchers: list of integers,
        @order: integer,
        @desciption: string
    
    '''
    templ = Template(filename='processes/'+t+'.json')  ## create a mako template
    raw_root =  templ.render()
    plan = json.loads(raw_root)
    outputs = []
    last_order = 0
    found_tasks = False
    #print plan

    if plan.get('processes'):
        processes = OrderedDict(sorted(plan.get('processes').items(), key=sort_by_order))
        list_of_order_numbers = [processes.get(i).get('order') for i in processes.keys()]
        remainings = []
        multies = []
        plan['processes'] = processes
        for process in processes:
            depends = []
            _id = getUUID()
            plan['processes'][process]['uuid'] = _id

            po = int(plan['processes'][process]['order'])
            _this = {'name':process, 'uuid':_id, 'order':po}
            if list_of_order_numbers.count(po)>1:
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


            process_plan = render_process(plan['processes'][process]['template'])

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
                del(plan['processes'][process])


    if plan.get('tasks'):
        tasks = OrderedDict(sorted(plan.get('tasks').items(), key=sort_by_order))
        list_of_order_numbers = [tasks.get(i).get('order') for i in tasks.keys()]
        remainings = []
        multies = []
        plan['tasks'] = tasks
        for task in tasks:
            if not task:
                continue
            _id = getUUID()
            depends = outputs
            plan['tasks'][task]['uuid'] = _id

            to = int(plan['tasks'][task]['order'])
            _this = {'name':task, 'uuid':_id, 'order':to}
            if list_of_order_numbers.count(to)>1:
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
            last_order = max(to, last_order)

            if plan['tasks'][task].get('template'):
                process_task = render_task(plan['tasks'][task]['template'])
                if process_task:
                    found_tasks = True
                    plan['tasks'][task]['plan'] = process_task
            else:
                del(plan['tasks'][task])
                print('\tWarning: task "%s -> %s" has not any template!' % (t, task))


    #if not found_tasks:
    #    return {}

    with open('plan.json', 'wb') as f:
        f.write(json.dumps(plan, sort_keys=True, indent=4))
    return plan



def render_task(t):
    '''lets see what will happen'''
    templ = Template(filename='tasks/'+t+'.json')  ## create a mako template
    raw_process = templ.render()
    task = json.loads(raw_process)
    return task


def flatten(plan):
    flat = {"tasks":[]}
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
            #if target.get('tasks'):
                flat['tasks'].append(process.get('tasks'))
        target = target.get('processes')


    with open('flat.json', 'wb') as f:
        f.write(json.dumps(flat, sort_keys=True, indent=4))
    return flat


if __name__ == '__main__':
    character_preproduction_template = "character_preproduction"
    plan = render_process(character_preproduction_template)
    flat = flatten(plan)




    
    

