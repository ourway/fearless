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



from opensource.dal import *
from uuid import uuid4
import datetime
now = datetime.datetime.utcnow



def getdb():
    db = DAL('sqlite://storage.sqlite', 
             check_reserved=['all'], 
             folder="database", pool_size=0, lazy_tables = True)


    db.define_table('auth_user',
        Field('datetime', 'datetime', default=now()),
        Field('uuid', 'string', default=uuid4()),
        Field('name', 'string', required=True, notnull=True, unique=True),
        Field('first_name', 'string', required=True, notnull=True),
        Field('last_name', 'string', required=True, notnull=True),
        Field('email', 'string', required=True, notnull=True, unique=True),
        Field('pswd', 'password', required=True),
        Field('avatar', 'string', default='default_avatar.png'),
        Field('last_login', 'datetime'),
                    )


    db.define_table('departement',
        Field('datetime', 'datetime', default=now()),
        Field('uuid', 'string', default=uuid4()),
        Field('name', 'string', required=True, notnull=True, unique=True),
        Field('icon', 'string', default='default_avatar.png'),
                    )


    db.define_table('prefs',
        Field('datetime', 'datetime', default=now()),
        Field('name', length=32),
        Field('value', length=356),
        Field('person', db.auth_user),
        )


    db.define_table('process',
        Field('uuid', length=64, default=uuid4()),
        Field('name','string'),
        Field('islocked','boolean',default=False),
        Field('isfinished','boolean',default=False),
        Field('isreported','boolean',default=False),
        )

    db.define_table('download',
        Field('uuid', length=64, default=uuid4()),
        Field('url','string'),
        Field('islocked','boolean',default=False),
        Field('isfinished','boolean',default=False),
        Field('isreported','boolean',default=False),
        Field('length','integer',default=0),
        Field('person', db.auth_user),
        )


    db.define_table('item',
        Field('uuid', length=64, default=uuid4()),
        Field('creation_date', 'datetime', default=now()),
        Field('owner', db.auth_user),
        Field('pid',  length=256),
        Field('type', length=32),
        Field('likes', 'list:reference auth_user', default=[]),
        Field('shared_with', 'list:reference auth_user', default=[]),
        Field('publish_code', length=64, default=uuid4()),
        Field('description','text'),
        Field('vfiles', 'list:reference vfile', default=[]),
        Field('type', length=64)
        )



    return db

if __name__ == '__main__':
    db = getdb()

