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
                        data = json.loads(showInfo)
                        assetId = data.get('id')
                        command = data.get('command')
                        frames = data.get('frames')
                        want_to_be_master = data.get('i_want_to_be_master')
                        client = json.loads(showInfo).get('client') or req.env.get('HTTP_X_FORWARDED_FOR')
                        if assetId:
                            master = r.get('show_%s_master'%assetId)
                            if want_to_be_master: # Asset is unlocked
                                if master and str(client) != master:  ## check if not other master
                                   pass
                                else:
                                    r.set('show_%s_master'%assetId, str(client))
                                    r.expire('show_%s_master'%assetId, 1)
                                    r.set('show_%s_command'%assetId, command)
                                    r.set('show_%s_frames'%assetId, frames)
                                    r.expire('show_%s_command'%assetId, 1)
                                    r.expire('show_%s_frames'%assetId, 1)
                            command = r.get('show_%s_command'%assetId)
                            frames = r.get('show_%s_frames'%assetId)
                                #if r.getset('show_%s_%s_latest_command'% (assetId, client), command) == command:
                                #    command = None
                                #if r.getset('show_%s_%s_latest_frames'% (assetId, client), frames) == frames:
                                #    frames = None
                                #if master == str(client): ## dont send command to its issuer
                                #    command = None
                                #    frames = None
                            wsock.send(json.dumps({"master" : r.get('show_%s_master'%assetId),
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
