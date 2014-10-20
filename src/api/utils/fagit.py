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


class GIT(object):

    def __init__(self, filepath, wt=None):

        gitdir = os.path.abspath('../../REPO')
        if not os.path.isdir(gitdir):
            os.makedirs(gitdir)

        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        git = sh.git
        self.wt = os.path.dirname(self.filepath)
        if not os.path.isdir(self.wt):
            os.makedirs(self.wt)
        self.git = git.bake(_cwd=self.wt,
                            _piped="err",
                            git_dir=gitdir,
                            work_tree=self.wt)
        self.git.init()

    def add(self, message=''):
        self.git.add(self.basename)
        self.git.commit(m='"{message} | Added {f} to repository"'.format(
            message=message, f=self.basename))

    def recover(self):
        self.git.checkout(self.basename, f=True)
