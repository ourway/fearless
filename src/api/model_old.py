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


from pony.orm import *
from uuid import uuid4
from datetime import datetime

#############
##########
from riak import RiakClient
from elasticsearch import Elasticsearch
ES = Elasticsearch()

from riak import RiakObject
TeamClient = RiakClient(pb_port=8087, protocol='pbc')
print "Creating riak connection on port 8087"
# TeamClient.create_search_index('fateam_assets')
file_bucket = TeamClient.bucket('AssetDB01')
# file_bucket.enable_search()
##########
##############
db = Database('sqlite', 'database/database.sqlite', create_db=True)
now = datetime.utcnow


def getUUID():
    return str(uuid4())

############################################################
###########################################################


class Person(db.Entity):
    name = Required(unicode, unique=True)
    email = Required(str, unique=True)
    password = Required(str)
    token = Required(str, default=getUUID())
    created_on = Required(datetime, default=now())
    modified_on = Optional(datetime, default=now())
    first_name = Optional(unicode)
    last_name = Optional(unicode)
    reports = Set("Report")
    groups = Set("Group")


class Report(db.Entity):
    created_on = Required(datetime, default=now())
    body = Required(LongStr)
    person = Required(Person)


class Rule(db.Entity):
    name = Required(unicode, unique=True)
    groups = Set("Group")


class Group(db.Entity):
    name = Required(unicode, unique=True)
    persons = Set(Person)
    rule = Required(Rule)


############################################################
###########################################################
# generate mapping
db.generate_mapping(create_tables=True)

# Lets create some defualt rules
default_rules = ['admin', 'user', 'guest', 'manager']
with db_session:
    for rulename in default_rules:
        if not Rule.get(name=rulename):
            newrule = Rule(name=rulename)
    commit()


if __name__ == '__main__':
    pass
