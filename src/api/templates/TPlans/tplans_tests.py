
from mako.template import Template
import json as json
from uuid import uuid4  # for random guid generation
import base64
from collections import OrderedDict


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
    templ = Template(filename=t+'.json')  ## create a mako template
    raw_root =  templ.render()
    plan = json.loads(raw_root)
    outputs = []
    last_order = 0

    #print plan

    if plan.get('processes'):
        processes = OrderedDict(sorted(plan.get('processes').items(), key=sort_by_order))
        plan['processes'] = processes
        for process in processes:
            _id = getUUID()
            plan['processes'][process]['id'] = _id
            po = int(plan['processes'][process]['order'])
            if  po > last_order:
                plan['processes'][process]['depends_on'] = outputs
                outputs = [{'name':process, 'id':_id}]
            elif po == last_order:
                outputs.append({'name':process, 'id':_id})
            if po > last_order:
                last_order = po

            process_plan = render_process(plan['processes'][process]['template'])
            plan['processes'][process]['plan'] = process_plan
    if plan.get('tasks'):
        tasks = OrderedDict(sorted(plan.get('tasks').items(), key=sort_by_order))
        plan['tasks'] = tasks
        for task in tasks:
            _id = getUUID()
            plan['tasks'][task]['id'] = _id
            po = int(plan['tasks'][task]['order'])
            if  po > last_order:
                plan['tasks'][task]['depends_on'] = outputs
                outputs = [{'name':process, 'id':_id}]
            elif po == last_order:
                outputs.append({'name':process, 'id':_id})
            if po > last_order:
                last_order = po
            process_task = render_task(plan['tasks'][task]['template'])
            plan['tasks'][task]['plan'] = process_task
    with open('plan.json', 'wb') as f:
        f.write(json.dumps(plan, sort_keys=True, indent=4))
    return plan



def render_task(t):
    '''lets see what will happen'''
    templ = Template(filename=t+'.json')  ## create a mako template
    raw_process = templ.render()
    task = json.loads(raw_process)
    return task



if __name__ == '__main__':
    character_preproduction_template = "character_preproduction"
    render_process(character_preproduction_template)




    
    

