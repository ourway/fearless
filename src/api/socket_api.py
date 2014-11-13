#!../../pyenv/bin/python
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


from gevent import monkey; monkey.patch_all()
from falcon_patch import falcon
from utils.syncshow import SyncShow
from utils.chat import Chat

            
app = falcon.API()
app.add_route('/media/syncshow', SyncShow())
app.add_route('/conn/chat', Chat())


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(("0.0.0.0", 5004), app,
                        handler_class=WebSocketHandler)
    server.serve_forever()
