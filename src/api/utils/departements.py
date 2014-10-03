#!/usr/bin/env python
# -*- coding: utf-8 -*-
_author = 'Farsheed Ashouri'
'''
   ___              _                   _ 
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an appology! 
Clean code is much better than Cleaner comments!
'''

import bottle
from model import getdb

dep_api=bottle.Bottle()
db = getdb()

@dep_api.post('/test')
def add_departments():
    '''Register a departement'''
    dep = db(db.departement.name == name).select().last()
    if not dep:
        dep = db.departement.insert(name=name)
        data = {'message': 'OK'}
    else:
        data = {'message': 'EXSISTED'}


def remove_departments():
    '''delete a departement'''
    dep = db(db.departement.name == name)
    if not dep.isempty():
        dep.delete()
        data = {'message': 'OK'}
    else:
        data = {'message': 'NOT EXSISTED'}




