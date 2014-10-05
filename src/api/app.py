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
from utils.assets import AssetSave, ListAssets, GetAsset
from utils.AAA import PersonManager

class ThingsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = "ok"



# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
things = ThingsResource()


# things will handle all requests to the '/things' URL path
app.add_route('/api/things', things)
app.add_route('/api/asset/save/{user}/{repo}', AssetSave())
app.add_route('/api/asset/list', ListAssets())
app.add_route('/api/asset/{key}', GetAsset())
app.add_route('/api/users', PersonManager())


if __name__ == '__main__':
    from werkzeug import run_simple
    run_simple('0.0.0.0', 5005, app, use_debugger=True, use_reloader=True)
