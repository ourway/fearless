#!/usr/bin/env python
# -*- coding: utf-8 -*-
_author = 'Farsheed Ashouri'
'''
   ___              _                   _
  / __\_ _ _ __ ___| |__   ___  ___  __| |
 / _\/ _` | '__/ __| '_ \ / _ \/ _ \/ _` |
/ / | (_| | |  \__ \ | | |  __/  __/ (_| |
\/   \__,_|_|  |___/_| |_|\___|\___|\__,_|

Just remember: Each comment is like an appology!
Clean code is much better than Cleaner comments!
'''

import falcon
import re


class Response(falcon.response.Response):
    def __init__(self):
        super(Response, self).__init__()
        self.extra_headers = list()
 
    def append_header(self, name, value):
        '''Fixes the problem of multiple Cookie headers.
            @input 
                name, value
 
            usage:
                resp.append_header('set-cookie', 'session-id=321654987654')
        '''
        self.extra_headers.append((name, value))
 
    def _wsgi_headers(self, media_type=None):
        header_list = super(Response, self)._wsgi_headers(media_type=media_type)
        for key, header in enumerate(header_list):
            if isinstance(header[1], list):
                header_list.pop(key)
                for val in header[1]:
                    header_list.append((header[0], val))
 
        return header_list + self.extra_headers
 


class Request(falcon.request.Request):
    def __init__(self, env):
        super(Request, self).__init__(env)

    def cookie(self, name):
        raw = self.headers.get('COOKIE')
        if not raw:
            return
        else:
            x = re.findall(re.compile(r'[; ]*'+ name + r'=([\w " \. = \d &]+)'), raw)
            if x:
                return x[0]


falcon.api.Response = Response
falcon.api.Request = Request
