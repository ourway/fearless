

import os
from sqlalchemy import create_engine  # for database
from sqlalchemy.orm import sessionmaker
from sqlalchemy_mptt import mptt_sessionmaker

from mixin import Base

db_path = ':memory:'
#db_path = 'database/studio.db'

try:
    db_dir = os.path.dirname(db_path)
    if not os.path.isdir(db_dir):
        os.makedirs(db_dir)
except OSError:
    pass

engine = create_engine('sqlite:///%s' % db_path, echo=False)
Session = mptt_sessionmaker(sessionmaker(bind=engine))
session = Session()
