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
db = DAL('sqlite://storage.sqlite', check_reserved=['all'], folder="database")
from uuid import uuid4
import datetime
now = datetime.datetime.utcnow

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

