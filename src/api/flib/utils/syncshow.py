#!../../../pyenv/bin/python
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


import json as json
from flib.models import r
from flib.utils.helpers import dumps
from geventwebsocket import WebSocketError


class SyncShow:

    def on_get(self, req, resp):
        """Handles GET requests"""
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        wsock = req.env.get('wsgi.websocket')
        #client = req.env.get('HTTP_X_FORWARDED_FOR')
        if wsock:
            while True:
                try:
                    '''AssetInfo should be something like this:
                        {"id":5,"command":"hey()"}
                    '''
                    showInfo = wsock.receive()
                    if not showInfo:
                        continue
                    data = json.loads(showInfo)
                    assetId = data.get('id')
                    command = data.get('command')
                    frame = data.get('frame')
                    note = data.get('note')
                    slide = data.get('slide')
                    want_to_be_master = data.get('i_want_to_be_master')
                    client = json.loads(showInfo).get(
                        'client') or req.env.get('HTTP_X_FORWARDED_FOR')
                    if assetId:
			print assetId
                        if not str(client) in r.lrange('show_%s_watchers' % assetId, 0, -1):
                            r.rpush('show_%s_watchers' % assetId, client)
                            r.expire('show_%s_watchers' % assetId, 1)
                        master = r.get('show_%s_master' % assetId)
                        if want_to_be_master:  # Asset is unlocked
                            # check if not other master
                            if master and str(client) != master:
                                pass
                            else:
                                r.set('show_%s_master' % assetId, str(client))
                                r.set('show_%s_command' % assetId, command)
                                r.set('show_%s_frame' % assetId, frame)
                                r.set('show_%s_note' % assetId, note)
                                r.set('show_%s_slide' % assetId, slide)
                                r.expire('show_%s_master' % assetId, 1)
                                r.expire('show_%s_command' % assetId, 1)
                                r.expire('show_%s_frame' % assetId, 1)
                                r.expire('show_%s_note' % assetId, 1)
                                r.expire('show_%s_slide' % assetId, 1)

                        command = r.get('show_%s_command' % assetId)
                        frame = r.get('show_%s_frame' % assetId)
                        note = r.get('show_%s_note' % assetId)
                        slide = r.get('show_%s_slide' % assetId)
                        watchers = r.lrange(
                            'show_%s_watchers' % assetId, 0, -1)
                        #note = json.loads(note)
                        if r.getset('show_%s_%s_latest_command' % (assetId, client), command) == command:
                            command = None
                        if r.getset('show_%s_%s_latest_frame' % (assetId, client), frame) == frame:
                            frame = 'KEEP'
                        if r.getset('show_%s_%s_latest_note' % (assetId, client), note) == note:
                            note = 'KEEP'

                        # if master == str(client): ## dont send command to its issuer
                            #    command = None
                            #    frames = None
                        wsock.send(dumps({"master": r.get('show_%s_master' % assetId),
                                          "frame": frame, "command": command, "note": note,
                                          "slide": slide, 'watchers': watchers}))

                except (WebSocketError, KeyboardInterrupt):
                    break
