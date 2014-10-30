#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob
import time

db = dict()
cmd = 'tj3 -o html/ {file}'

def update_mtime():
    for i in glob.glob('*.tjp'):
        db[i] = os.stat(i).st_mtime


def watch():
    while 1:
        update_mtime()
        for file in db:
            if time.time() - db.get(file) <= 1:
                os.system(cmd.format(file=file))
                print '\tFile "%s" rendered.' % file
        time.sleep(1)


if __name__ == '__main__':
    watch()
