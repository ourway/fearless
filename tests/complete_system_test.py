#!../pyenv/bin/python

import sys, os
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/api'))
sys.path.append(module_path)



from models import *

'''We have a client'''
client = Client(name='pooyamehr')
''' Lets create few users '''
user1 = User(email='rodmena@me.com', password='rrferl', active=True)
user2 = User(email='farsheed.ashouri@gmail.com', password='rrferl', active=True)
''' Our main project '''
proj = Project(name='Fearless project 1')
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

task1 = Task(title="rig")
task1.resources.append(user1)
task2 = Task(title="model")
task2.resources.append(user2)
task2.resources.append(user1)
task2.project=proj
task1.depends_on.append(task2)

task1.start = '2014-1-1'
task2.start = '2013-12-15'
task2.end   = '2014-1-15'
task1.end   = '2014-1-20'

session.add_all([task1, user1, user2, proj, client, repo1, nuke_section, maya_section])
try:
    session.commit()
    import shutil
    print proj.tasks
    #print maya_section.assets
    shutil.copyfileobj(maya_section.archive, open('maya_section.tar', 'w'))
except Exception, e:
    print e
finally:
    os.system('rm -rf database')

