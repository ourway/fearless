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
from base64 import encodestring
from string import ascii_letters
from cStringIO import StringIO
import zlib


def fix_name(name):
    for i in '()[]{} ":,./':
        name = name.replace(i, '_')
    for i in name:
        if i not in ascii_letters:
            name.replace(i, encodestring(i))
    return name


class GIT(object):

    def __init__(self, filepath, wt=None):

        self.filepath = filepath
        git = sh.git
        if not wt:
            self.wt = os.path.dirname(self.filepath)
        else:
            self.wt = wt
        if filepath != '.':
            self.basename = os.path.relpath(filepath, self.wt)
            #self.basename = fix_name(self.basename)

        else:
            self.basename = '.'
        if not os.path.isdir(self.wt):
            os.makedirs(self.wt)
        self.git = git.bake(_cwd=self.wt,
                            _ok_code=[128, 1]
                            #_piped="err",
                            # git_dir=gitdir,
                            # work_tree=self.wt
                            )
        i = self.git.init()

    def add(self, message='', version=1):
        a = self.git.add(self.basename)
        c = self.git.commit(m="{message} | {f} version {v}".format(
            message=message, f=fix_name(self.basename), v=version))
        t = self.tag('%s_v%s' % (fix_name(self.basename), version))

    def recover(self):
        c = self.git.checkout(self.basename, f=True)

    @property
    def status(self):
        pass

    def tag(self, tag):
        tag = fix_name(tag)
        t = self.git.tag(tag)

    def archive(self, commit='HEAD'):
        '''returns a file object containing zip version of files'''
        f = StringIO()
        a = self.git('archive', '--format', 'tar', commit)
        f.write(a.stdout)
        f.seek(0)
        return f
