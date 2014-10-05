#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an apology!
Clean code is much better than Cleaner comments!
'''

#import sys, os
#sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from pony.orm import *
from model import Person, Report, Group, Rule

import falcon

class PersonManager:
    def on_post(self, req, resp):
        '''Add a user to database'''
        name = req.get_param('name')
        email = req.get_param('email')
        password = req.get_param('password')
        first_name = req.get_param('first_name')
        last_name = req.get_param('last_name')
        if name and email and password:
            with db_session:
                user = select(p for p in Person if (p.name==name or p.email==email))[:]
                if not user:

                    resp.status = falcon.HTTP_201
                    user = Person(  name=name,
                                    email=email,
                                    password=password)
                    if first_name: user.first_name = first_name.strip()
                    if last_name: user.last_name = first_name.strip()
                    user_rule = Rule.get(name='user')
                    user.groups.create(name=name, rule=user_rule)
                    commit()
                    print user.groups
                    resp.body = 'User "%s" successfully created.' % name
                else:
                    resp.status = falcon.HTTP_202
                    resp.body = 'User/Email is available'
        #resp.body = 'post'

    def on_get(self, req, resp):
        '''Authenticate a user'''
        resp.body = 'I am in get mode'



