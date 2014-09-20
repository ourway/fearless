#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#

# sysctl -n -w fs.inotify.max_user_watches=16384

import asyncore
import pyinotify
import os
import sh
wm = pyinotify.WatchManager()  # Watch ManagerIN_ATTRIB
path = '/home/farsheed/Public/Desktop/mytest'
git = sh.git.bake(_cwd=path)

'''
IN_ACCESS – File was accessed
IN_ATTRIB – Metadata changed (permissions, timestamps, extended attributes, etc.)
IN_CLOSE_WRITE – File opened for writing was closed
IN_CLOSE_NOWRITE – File not opened for writing was closed
IN_CREATE – File/directory created in watched directory
IN_DELETE – File/directory deleted from watched directory
IN_DELETE_SELF – Watched file/directory was itself deleted
IN_MODIFY – File was modified
IN_MOVE_SELF – Watched file/directory was itself moved
IN_MOVED_FROM – File moved out of watched directory
IN_MOVED_TO – File moved into watched directory
IN_OPEN – File was opened
'''
# watched events
#mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
mask =   pyinotify.IN_CLOSE_WRITE | \
         pyinotify.IN_ATTRIB | \
         pyinotify.IN_CREATE | \
         pyinotify.IN_DELETE | \
         pyinotify.IN_MODIFY | \
         pyinotify.IN_MOVE_SELF | \
         pyinotify.IN_MOVED_FROM | \
         pyinotify.IN_MOVED_TO | \
         pyinotify.IN_ACCESS
        


SUFFIXES = {".md", ".markdown"}
class EventHandler(pyinotify.ProcessEvent):

    #def __call__(self, event):
    #    if not suffix_filter(event.name):
    #        super(EventHandler, self).__call__(event)
    #prevent = SUFFIXES 
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname


#    def process_IN_ATTRIB(self, event):
#        print "attrib:", event.pathname

#    def process_IN_ACCESS(self, event):
#        print "aceess:", event.pathname



#    def process_IN_DELETE(self, event):
#        print "Removing:", event.pathname

#    def process_IN_MOVED_FROM(self, event):
#        print "Moved from:", event.pathname

#    def process_IN_MOVE_SELF(self, event):
#        print "moved self:", event.pathname

#    def process_IN_MOVED_TO(self, event):
#        print "moved to:", event.pathname


    def process_IN_CLOSE_WRITE(self, event):
        print "Write Finished:", event.pathname
        f = os.path.relpath(event.pathname, path)
        if os.path.isfile(event.pathname) and '.git' not in f :
            git.add(f)
            git.commit(m='new file "%s" added.'%f)

notifier = pyinotify.AsyncNotifier(wm, EventHandler(), timeout=10)
wdd = wm.add_watch(path, mask, rec=True)

asyncore.loop()
