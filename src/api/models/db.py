

import os
from sqlalchemy import create_engine  # for database
from sqlalchemy.orm import sessionmaker
from sqlalchemy_mptt import mptt_sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from mixin import Base

#db_path = ':memory:'
#db_path = 'database/studio.db'
db_path = os.path.join( os.path.dirname(__file__), '../database/studio.db')

try:
    db_dir = os.path.dirname(db_path)
    if not os.path.isdir(db_dir):
        os.makedirs(db_dir)
except OSError:
    pass

engine = create_engine('sqlite:///%s' % db_path, echo=False, encoding='utf-8', poolclass=SingletonThreadPool)
#engine.raw_connection().connection.text_factory = str
Session = mptt_sessionmaker(sessionmaker(bind=engine))
session = Session()
