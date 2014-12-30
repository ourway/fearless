

import os
from sqlalchemy import create_engine  # for database
from sqlalchemy.orm import sessionmaker
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

msqldbname = 'fearless1'
#msql = 'mysql+mysqldb://root:rrferl@localhost/%s?charset=utf8&use_unicode=1' % msqldbname
msql = 'mysql+mysqldb://root:rrferl@localhost/%s' % msqldbname

sqlite = 'sqlite:///%s' % db_path
postgres = 'postgresql+psycopg2://user:password@/dbname'

DB = msql



#engine = create_engine(DB, echo=False, convert_unicode=True)
engine = create_engine(DB, echo=False, convert_unicode=True, pool_recycle=3600)




#engine = create_engine("postgresql+psycopg2://farsheed:rrferl@localhost:5432/fearless2")
#engine.raw_connection().connection.text_factory = str
#Session = mptt_sessionmaker(sessionmaker(bind=engine, expire_on_commit=False))
Session = sessionmaker(bind=engine)

session = Session()
