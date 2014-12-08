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


user1 = User(email='farsheed.ashouri@gmail.com', password='rrferl', active=True, firstname='admin2', lastname='admin2')
user2 = User(email='mehdieyazdani@gmail.com', password='123456', active=True, firstname='Mehdi', lastname='Yazdani')
user3 = User(email='mostafarayaneh@gmail.com', password='123456', active=True, firstname='Morteza', lastname='Gaamari')
user4 = User(email='amirgholamzadeh@gmail.com', password='123456', active=True, firstname='Amir', lastname='Gholam Zadeh')
user5 = User(email='mostafa_khaleghi64@yahoo.com', password='123456', active=True, firstname='Mostafa', lastname='Khalegi')
user6 = User(email='hamedanime@gmail.com', password='123456', active=True, firstname='Hamed', lastname='Behroozi')
user7 = User(email='shahriyar.shahramfar@gmail.com', password='123456', active=True, firstname='Bijan', lastname='Shahramfar')
user8 = User(email='mhd.kheirandish@yahoo.com', password='123456', active=True, firstname='Mohammad', lastname='Kheirandish')
user9 = User(email='mehrdadshahverdi81@gmail.com', password='123456', active=True, firstname='Mehrdad', lastname='Shahverdi')
user10 = User(email='firoozeh.imany@gmail.com', password='123456', active=True, firstname='Firoozeh', lastname='Imani')
user11 = User(email='parima.1367@yahoo.com', password='123456', active=True, firstname='Parima', lastname='Daliri')
user12 = User(email='mina.nazaralhooee@gmail.com', password='123456', active=True, firstname='Mina', lastname='Nazari')
user13 = User(email='arashentezami3d@gmail.com', password='123456', active=True, firstname='Arash', lastname='Entezami')
user14 = User(email='zara.erfani@yahoo.com', password='123456', active=True, firstname='Zahra', lastname='Erfani')
user15 = User(email='negarahmadi@gmail.com', password='123456', active=True, firstname='Negar', lastname='Ahmadi')
user16 = User(email='merfanparsapour@yahoo.com', password='123456', active=True, firstname='Erfan', lastname='Parsapour')
user17 = User(email='f.shamayel@gmail.com', password='123456', active=True, firstname='Farshad', lastname='Shamayel')
user18 = User(email='amin.zarouni@gmail.com', password='123456', active=True, firstname='Amin', lastname='Zarouni')
user19 = User(email='khalil66@gmail.com', password='123456', active=True, firstname='Khalil', lastname='Khaliliyan')
user20 = User(email='hamid2117@gmail.com', password='123456', active=True, firstname='Hamid', lastname='Lak')
user21 = User(email='mepayam@gmail.com', password='123456', active=True, firstname='Payam', lastname='Memar')
user22 = User(email='alishahdad1353@yahoo.com', password='123456', active=True, firstname='Ali', lastname='Shahdad')
user23 = User(email='hamid_sohrabi_vale@yahoo.com', password='123456', active=True, firstname='Hamid', lastname='Sohrabi')
user24 = User(email='rangekhod.2000@yahoo.com', password='123456', active=True, firstname='Majid', lastname='Majidi')
user25 = User(email='banomo1282@yahoo.com', password='123456', active=True, firstname='Bahare', lastname='Mogaddam')
user26 = User(email='amirhoseinkasraee@yahoo.com', password='123456', active=True, firstname='AmirHossein', lastname='Kasrayi')
user27 = User(email='nsns_1300@yahoo.com', password='123456', active=True, firstname='Nasim', lastname='Sadegi')
user28 = User(email='zahra.mansouriyeh@gmail.com', password='123456', active=True, firstname='Zahra', lastname='Mansooriye')
user29 = User(email='alenhue@gmail.com', password='123456', active=True, firstname='Arash', lastname='Mogaddam')


''' Our main project '''
proj = Project(name='Fearless project 1')
proj2  = Project(name='fuooo')
proj.end = '2015-5-30'
proj2.end = '2015-12-30'
#proj.tickets.append('i am a ticket')
proj.lead = user1
proj2.lead = user2


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

nuke_section = Collection(name='composite', template='nuke', path='some3ddata')
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
sellme.effort = 7
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
animate.effort = 16



#task1.start = '2014-1-1'
rig.effort= 18

#task2.start = '2014-2-1'
model.duration= 15


session.add_all([ user1, user2, user3, user4, user5, user6, user7, user8, user9,
                 user10, user11, user12, user13, user14, user15, user16, user17,
                 user18, user19, user20, user21, user22, user23, user24, user25,
                    user26, user27, user28, user29, 
                 model, proj, client, repo1, nuke_section, maya_section, rig, research,
                 cleanup, sellme])
session.commit()
    #import shutil
#print animate.get_tree(session, json=True)

#proj.plan


print session.query(Project).join(Task).all()

session.commit()
print proj.reports

    #print maya_section.assets
    #shutil.copyfileobj(maya_section.archive, open('maya_section.tar', 'w'))

