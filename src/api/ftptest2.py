from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
#from pyftpdlib.servers import MultiprocessFTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.authorizers import UnixAuthorizer
from pyftpdlib.filesystems import UnixFilesystem


class MyHandler(FTPHandler):

    def on_connect(self):
        print "%s:%s connected" % (self.remote_ip, self.remote_port)

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_login(self, username):
        # do something when user login
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        print 'I recived a file!!!!!', file
        pass

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)


def main():
    #authorizer = DummyAuthorizer()
    authorizer = UnixAuthorizer(rejected_users=["root"], 
                require_valid_shell=False)

    authorizer.override_user('bijan', homedir='/home/share')
    authorizer.override_user('yazdani', homedir='/home/share',  perm='elradfmw')
    #authorizer.add_anonymous(homedir='/share/public')

    handler = MyHandler
    handler.authorizer = authorizer
    handler.use_send_file=True
    #handler.abstracted_fs = UnixFilesystem
    server = FTPServer(('', 2121), handler)
    #server = MultiprocessFTPServer(('', 2121), handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
