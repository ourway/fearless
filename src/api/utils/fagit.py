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

'''
@desc: tasks.py
@c: Chista Co
@author: F.Ashouri
@version: 0.1.8
'''
import os
import sh



class GIT(object):
    def __init__(self, filepath):

        gitdir = os.path.abspath('../../REPO')
        if not os.path.isdir(gitdir):
            os.makedirs(gitdir)
        self.filepath = filepath
        self.basename = os.path.basename(filepath)
        git = sh.git
        wt = os.path.dirname(self.filepath)
        self.git = git.bake(_cwd=wt, 
                            _piped="err",
                            git_dir=gitdir,
                            work_tree=wt)
        self.git.init()
        
    def add(self):
        self.git.add(self.basename)
        self.git.commit(m='Added {f} to repository'.format(f=self.basename))

    def recover(self):
        self.git.checkout(self.basename, f=True)

