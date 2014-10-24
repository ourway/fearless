#!../pyenv/bin/python

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

asset = Asset(key='mayafile')
asset.users.append(user2)
import pdb; pdb.set_trace()
import pdb; pdb.set_trace()
repo1 = Repository(name='happy', path='/home/farsheed/Desktop/dout')
proj.repository = repo1

session.add_all([user1, user2, proj, client, asset, repo1])
session.commit()

print asset.users

