

import os
from sqlalchemy import create_engine, event  # for database
from sqlalchemy.orm import scoped_session,  sessionmaker
from sqlalchemy.exc import DisconnectionError

from sqlalchemy.pool import SingletonThreadPool
from flib.models.mixin import Base

#db_path = ':memory:'
#db_path = 'database/studio.db'
db_path = os.path.join(os.path.dirname(__file__), '../database/studio.db')

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


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise



#engine = create_engine(DB, echo=False, convert_unicode=True)
engine = create_engine(DB, echo=False, 
            convert_unicode=True, pool_recycle=3600,
                       pool_size=256, max_overflow=128)


event.listen(engine, 'checkout', checkout_listener)

#engine = create_engine("postgresql+psycopg2://farsheed:rrferl@localhost:5432/fearless2")
#engine.raw_connection().connection.text_factory = str
#Session = mptt_sessionmaker(sessionmaker(bind=engine, expire_on_commit=False))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
