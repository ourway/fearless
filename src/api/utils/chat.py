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

from geventwebsocket import WebSocketError


class Chat:

    def on_get(self, req, resp):
        wsock = req.env.get('wsgi.websocket')
        if wsock:
            while True:
                try:
                    data = wsock.receive()
                    wsock.send(data)

                except (WebSocketError, KeyboardInterrupt):
                    break
