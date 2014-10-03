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
import ujson
from model import getdb
from opensource.contenttype import contenttype
db=getdb()

def clean(req, resp, *kw):
    #print kw
    #print dir(db)
    db.commit()
    #db.close()


class Departements(object):
    @falcon.after(clean)
    def on_put(self, req, resp, name, **kw):
        '''Register a departement'''
        dep = db(db.departement.name==name).select().last()
        if not dep:
            dep = db.departement.insert(name=name)
            data = {'message':'OK'}
        else:
            resp.status = falcon.HTTP_400
            data = {'message':'EXSISTED'}

        resp.body = ujson.dumps(data)


    @falcon.after(clean)
    def on_delete(self, req, resp, name, **kw):
        '''delete a departement'''
        dep = db(db.departement.name==name)
        if not dep.isempty():
            dep.delete()
            data = {'message':'OK'}
        else:
            resp.status = falcon.HTTP_400
            data = {'message':'NOT EXSISTED'}

        resp.body = ujson.dumps(data)



