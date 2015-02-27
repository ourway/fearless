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


import falcon
from flib.models import ddb


class GetNote:

    def on_get(self, req, resp, key):
        obj = ddb.get(key)
        if obj.data:
            resp.body = {'note': obj.data.get('note_s')}


class SetNote:

    def on_put(self, req, resp, key):
        value = req.stream.read()
        data = {'note_s': value}
        obj = ddb.new(key, data).store()
        resp.body = {'note': obj.data.get('note_s')}


class SearchNote:

    def on_post(self, req, resp, query):
        res = ddb.search('note_s:*%s*' % query)['docs']
        data = []
        for result in res:
            data.append({result.get('_yz_rk'): result.get('note_s')})
        resp.body = data
