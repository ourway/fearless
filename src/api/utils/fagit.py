#!/usr/bin/env python
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


import os
import sh
from cStringIO import StringIO
import zlib


class GIT(object):

    def __init__(self, filepath, wt=None):

        gitdir = os.path.abspath('../../REPO')
        if not os.path.isdir(gitdir):
            os.makedirs(gitdir)
        self.filepath = filepath
        git = sh.git
        if not wt:
            self.wt = os.path.dirname(self.filepath)
        else:
            self.wt = wt
        if filepath != '.':
            self.basename = os.path.relpath(filepath, self.wt)
        else:
            self.basename = '.'
        if not os.path.isdir(self.wt):
            os.makedirs(self.wt)
        self.git = git.bake(_cwd=self.wt,
                            _piped="err",
                            # git_dir=gitdir,
                            # work_tree=self.wt
                            )
        self.git.init()

    def add(self, message=''):
        self.git.add(self.basename)
        self.git.commit(m="{message} | Added {f} to repository".format(
            message=message, f=self.basename))

    def recover(self):
        self.git.checkout(self.basename, f=True)

    @property
    def status(self):
        pass

    def tag(self, tag):
        self.git.tag(tag)

    def archive(self, commit='HEAD'):
        '''returns a file object containing zip version of files'''
        f = StringIO()
        a = self.git('archive', '--format', 'tar', commit)
        f.write(a.stdout)
        f.seek(0)
        return f
