#!../../pyenv/bin/python

from gevent import monkey; monkey.patch_all()
from falcon_patch import falcon
from models import r
import ujson as json

class SyncShow:

    def on_get(self, req, resp):
        """Handles GET requests"""
        # resp.set_header('Set-Cookie','fig=newton; Max-Age=200')
        # print req.get_header('Cookie')
        wsock = req.env.get('wsgi.websocket')
        client = req.env.get('HTTP_ORIGIN')
        #client = req.env.get('HTTP_X_FORWARDED_FOR')
        if wsock:
            while True:
                try:
                    '''AssetInfo should be something like this:
                        {"id":5,"command":"hey()"}
                    '''
                    showInfo = wsock.receive()
                    try:
                        assetId = json.loads(showInfo).get('id')
                        command = json.loads(showInfo).get('command')
                        frames = json.loads(showInfo).get('frames')
                        client = json.loads(showInfo).get('client') or req.env.get('HTTP_X_FORWARDED_FOR')
                        if assetId:
                            if not r.get('show_%s_lock'%assetId): # Asset is unlocked
                                r.set('show_%s_lock'%assetId, str(client))
                                r.expire('show_%s_lock'%assetId, 30)
                                r.set('show_%s_command'%assetId, command)
                                r.set('show_%s_frames'%assetId, frames)
                                r.expire('show_%s_command'%assetId, 2)
                                r.expire('show_%s_frames'%assetId, 2)
                            else: # Asset is locked
                                master = r.get('show_%s_lock'%assetId)
                                if (str(client) == master) and command:
                                    r.set('show_%s_command'%assetId, command)
                                    r.set('show_%s_frames'%assetId, frames)
                                    r.expire('show_%_command'%assetId, 2)
                                    r.expire('show_%_frames'%assetId, 2)
                                command = r.get('show_%s_command'%assetId)
                                frames = r.get('show_%s_frames'%assetId)
                                #if r.getset('show_%s_%s_latest_command'% (assetId, client), command) == command:
                                #    command = None
                                #if r.getset('show_%s_%s_latest_frames'% (assetId, client), frames) == frames:
                                #    frames = None
                                #if master == str(client): ## dont send command to its issuer
                                #    command = None
                                #    frames = None
                            wsock.send(json.dumps({"lock" : r.get('show_%s_lock'%assetId),
                                                   "frames":frames, "command":command}))

                    except (ValueError, TypeError):
                        pass

                except (WebSocketError, KeyboardInterrupt) :
                    break
            
app = falcon.API()
syncshow = SyncShow()
app.add_route('/media/syncshow', syncshow)


if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket import WebSocketError
    from geventwebsocket.handler import WebSocketHandler
    server = WSGIServer(("0.0.0.0", 5004), app,
                        handler_class=WebSocketHandler)
    server.serve_forever()
