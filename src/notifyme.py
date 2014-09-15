#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#
# See: http://github.com/seb-m/pyinotify/wiki/Tutorial
#

# sysctl -n -w fs.inotify.max_user_watches=16384

import asyncore
import pyinotify
import os
wm = pyinotify.WatchManager()  # Watch Manager
# watched events
#mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
mask = pyinotify.IN_CLOSE_WRITE


SUFFIXES = {".md", ".markdown"}
class EventHandler(pyinotify.ProcessEvent):

    #def __call__(self, event):
    #    if not suffix_filter(event.name):
    #        super(EventHandler, self).__call__(event)
    #prevent = SUFFIXES 
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

    def process_IN_MODIFY(self, event):
        print "Modifying:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "Write Finished:", event.pathname

notifier = pyinotify.AsyncNotifier(wm, EventHandler(), timeout=10)
wdd = wm.add_watch('/home/farsheed/Public/Desktop', mask, rec=True)

asyncore.loop()
