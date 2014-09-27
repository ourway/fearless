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

import falcon
import ujson
import uwsgi
from opensource.contenttype import contenttype
from utils.departements import Departements
from utils.downloads import Downloads
from utils.assets import Assets
from utils.users import Login, Register, Recover
from utils.reports import Mailer

class home_route(object):
    '''A very basic search function for DPM'''
    #@falcon.before(check_api_version)
    def on_get(self, req, resp, **kw):
        """Handles GET requests"""
        data = {'body': 'This is a great api page'}
        resp.body = ujson.dumps(data)


app = falcon.API()
home = home_route()

app.add_route('/api/', home)
app.add_route('/api/departement/{name}/', Departements())
app.add_route('/api/download/', Downloads())
app.add_route('/api/users/login', Login())
app.add_route('/api/users/register', Register())
app.add_route('/api/users/recover', Recover())


#wget 127.0.0.1:5000/api/asset?path=/home/farsheed/Public/1bbd9cfd81be34cecd34681b0e744ce4.jpg@20f569287a087e3aec82e806cd8d9840



app.add_route('/api/asset/', Assets())
app.add_route('/api/reports/mail', Mailer())

