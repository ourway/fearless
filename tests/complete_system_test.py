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

'''OK, Not assign relations'''

client.users.append(user1)
client.projects.append(proj)


repo1 = Repository(name='happy', path='/home/farsheed/Desktop/dout')
proj.repository = repo1

''' Lets create a maya collection in this repository'''
maya_section = Collection(name='seq1', 
                schema='''
        {
            "folders":["scenes", "sourceimages", "data"], 
            "files":["workspace.mel", "readme.txt"],
            "ignore":"*.png"
        }
                          
        ''')
repo1.collections.append(maya_section)


session.add_all([user1, user2, proj, client, repo1])
session.commit()







os.system('rm -rf database')

