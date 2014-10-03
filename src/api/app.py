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
bottle.BaseRequest.MEMFILE_MAX = 2**31 # (or 2G)
import ujson
from opensource.contenttype import contenttype
from utils.assets import asset_api

app = bottle.Bottle()
app.mount('/asset', asset_api)


@app.route('/')
def test():
    return 'ok'



if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 8080))
    bottle.run(app, host='0.0.0.0', reloader=True,
               debug=True, port=5005)
    # from werkzeug import run_simple
    # run_simple('0.0.0.0', 5005, app, use_debugger=True, use_reloader=True)