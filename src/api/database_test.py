#!../../pyenv/bin/python
from models import *
a=Project(start="2014-11-22", end="2014-11-28" , name="my new web 2",lead_id="2")
session.add(a)
session.commit()
a.plan
session.commit()
