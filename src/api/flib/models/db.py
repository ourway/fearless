

import os
from sqlalchemy import create_engine, event, orm  # for database
from sqlalchemy.orm import scoped_session,  sessionmaker
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm.session import Session as SessionBase, object_session
from sqlalchemy.event.api import listen

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
#postgres = 'postgresql+psycopg2://user:password@/dbname'
postgres = 'postgresql+psycopg2://postgres:rrferl@localhost:5432/fearless1'
#postgresql+psycopg2://user:password@host:port/dbname

DB = msql
#DB = postgres


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




class SignallingSession(SessionBase):
    def __init__(self, **options):
        self._model_changes = {}
        SessionBase.__init__(self, **options)
 
class _SessionSignalEvents(object):
 
    def register(self):
        listen(SessionBase, 'after_commit', self.session_signal_after_commit)
        listen(SessionBase, 'after_rollback', self.session_signal_after_rollback)
 
    @staticmethod
    def session_signal_after_commit(session):
        if not isinstance(session, SignallingSession):
            return
        d = session._model_changes
        if d:
            for obj, change in d.values():
                if change == 'delete' and hasattr(obj, '__commit_delete__'):
                    obj.__commit_delete__()
                elif change == 'insert' and hasattr(obj, '__commit_insert__'):
                    obj.__commit_insert__()
                elif change == 'update' and hasattr(obj, '__commit_update__'):
                    obj.__commit_update__()
            d.clear()
 
    @staticmethod
    def session_signal_after_rollback(session):
        if not isinstance(session, SignallingSession):
            return
        d = session._model_changes
        if d:
            d.clear()
            
class _MapperSignalEvents(object):
 
    def __init__(self, mapper):
        self.mapper = mapper
 
    def register(self):
        listen(self.mapper, 'after_delete', self.mapper_signal_after_delete)
        listen(self.mapper, 'after_insert', self.mapper_signal_after_insert)
        listen(self.mapper, 'after_update', self.mapper_signal_after_update)
 
    def mapper_signal_after_delete(self, mapper, connection, target):
        self._record(mapper, target, 'delete')
 
    def mapper_signal_after_insert(self, mapper, connection, target):
        self._record(mapper, target, 'insert')
 
    def mapper_signal_after_update(self, mapper, connection, target):
        self._record(mapper, target, 'update')
 
    @staticmethod
    def _record(mapper, target, operation):
        s = object_session(target)
        if isinstance(s, SignallingSession):
            pk = tuple(mapper.primary_key_from_instance(target))
            s._model_changes[pk] = (target, operation)


# Usage
 
# this must happen only once
_MapperSignalEvents(orm.mapper).register()
_SessionSignalEvents().register()



#engine = create_engine(DB, echo=False, convert_unicode=True)
engine = create_engine(DB, echo=False,
            convert_unicode=True, pool_recycle=3600,
                       pool_size=256, max_overflow=128)



#engine = create_engine("postgresql+psycopg2://farsheed:rrferl@localhost:5432/fearless2")
#engine.raw_connection().connection.text_factory = str
#Session = mptt_sessionmaker(sessionmaker(bind=engine, expire_on_commit=False))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)




def before_flush(session, flush_context, instances):
    pass
    #for i in session.new:
    #    if i.__tablename__ == 'collection':
    #        collectionFinalFixes(i, session)



def after_flush(session):
    pass
    #for i in session.new:
    #    if i.__tablename__ == 'collection':
    #        createCollectionStandards(i, session)


event.listen(SessionBase, "before_commit", after_flush)
event.listen(SessionBase, "before_flush", before_flush)
event.listen(engine, 'checkout', checkout_listener)

