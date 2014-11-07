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
                        if assetId:
                            if not r.get('show_%s_lock'%assetId): # Asset is unlocked
                                r.set('show_%s_lock'%assetId, client)
                                r.expire('show_%s_lock'%assetId, 60)
                                r.set('show_%s_command'%assetId, command)
                                #r.expire('show_%s_frame'%assetId, 20)
                            else: # Asset is locked
                                master = r.get('show_%s_lock'%assetId)
                                if client == master and command:
                                    r.set('show_%s_command'%assetId, command)
                                    r.expire('show_%_command'%assetId, 4)
                                command = r.get('show_%s_command'%assetId)
                            wsock.send(json.dumps({"lock" : r.get('show_%s_lock'%assetId), "command":command}))

                    except ValueError:
                        pass

                except WebSocketError, KeyboardInterrupt :
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
