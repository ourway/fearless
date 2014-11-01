#!../pyenv/bin/python

import sys, os
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/api'))
sys.path.append(module_path)


from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased
from sqlalchemy.orm import subqueryload
from models import *
from mako.template import Template
import copy
'''We have a client'''
client = Client(name='pooyamehr')
''' Lets create few users '''
user1 = User(email='rodmena@me.com', password='rrferl', active=True, firstname='Farsheed', lastname='Ashouri')
user2 = User(email='farsheed.ashouri@gmail.com', password='rrferl', active=True)
''' Our main project '''
proj = Project(name='Fearless project 1')
proj2  = Project(name='fuooo')
proj.end = '2014-11-30'
proj2.end = '2014-12-30'
#proj.tickets.append('i am a ticket')
proj.lead = user2

'''OK, Not assign relations'''

client.users.append(user1)
client.projects.append(proj)


repo1 = Repository(name='happy', path='/home/farsheed/Desktop/my_asm_project')
repo1.project = proj

''' Lets create a maya collection in this repository'''
#maya_section = Collection(name='seq1',
#                schema='''
#        {
#            "folders":["scenes", "sourceimages", "data"],
#            "files":["workspace.mel", "readme.txt"],
#            "ignore":["*.png", "*.cache", "*.mc", "*.txt"]
#        }
#
#        ''')

nuke_section = Collection(name='composite', template='nuke')
maya_section = Collection(name='maya', template='maya', path='3d_data')

repo1.collections.append(maya_section)
repo1.collections.append(nuke_section)
#asset1 = Asset(key='testscenefile', path='scenes', ext='mb')
#asset1.collection = maya_section

rig = Task(title="rig")
animate = Task(title="animate")
animate.project=proj
sellme = Task(title="sell")
fock = Task(title="gogo", project=proj2)
fock.resources.append(user1)
sellme.resources.append(user2)
sellme.duration = 70
sellme.project = proj
rig.resources.append(user1)
model = Task(title="model")
model.resources.append(user2)
model.resources.append(user1)
rig.project=proj
model.project=proj

research = Task(title='research')
cleanup = Task(title='cleanup')
cleanup.project = proj
cleanup.parent = research
research.project=proj

rig.parent = model
model.parent = research
research.resources.append(user1)
rig.depends.append(model)
animate.depends.append(rig)
animate.resources.append(user2)


#task1.start = '2014-1-1'
rig.duration= 18

#task2.start = '2014-2-1'
model.duration= 15


session.add_all([model, user1, user2, proj, client, repo1, nuke_section, maya_section, rig, research, cleanup, sellme])
session.commit()
    #import shutil
#tj = Task.get_tree(session, json=True)

proj.plan

print session.query(Project).join(Task).all()



    #print maya_section.assets
    #shutil.copyfileobj(maya_section.archive, open('maya_section.tar', 'w'))

