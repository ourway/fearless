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

class home_route(object):
    '''A very basic search function for DPM'''
    #@falcon.before(check_api_version)
    def on_post(self, req, resp, **kw):
        """Handles GET requests"""
        data = {'body': 'This is a great api page'}
        resp.body = ujson.dumps(data)



app = falcon.API()
home = home_route()

app.add_route('/api/', home)

