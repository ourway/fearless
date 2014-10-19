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

from models import User, Group, Rule, session
import ujson as json

import falcon


class login:

    def on_post(self, req, resp):
        '''Add a user to database'''
        email = req.get_param('email')
        password = req.get_param('password')
        target = session.query(User).filter(User.email == email).first()
        if not target or not target.password == password:  # don't tell what's wrong!
            resp.body = json.dumps({'message':'error'})

        #print email
        #resp.body = 'OK'
