from sqlalchemy.orm import scoped_session, sessionmaker,Session
from sqlalchemy import create_engine
import database.db_tables as DB


class setup_database(object):
    sc_session: scoped_session

    def __init__(self, service_module):
        self.service = service_module
        self.initial_load()
        self.engine = create_engine('sqlite:///{}'.format(service_module.config_file['sqlite_database']['filename']),
                                    connect_args={'check_same_thread':False,'timeout':3000}, echo=False)
        DB.Base.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.sc_session = scoped_session(Session)

    def initial_load(self):
        engine = create_engine('sqlite:///{}'.format(self.service.config_file['sqlite_database']['filename']),
                               connect_args={'check_same_thread': True, 'timeout': 3000}, echo=False)
        DB.version.versionBase.metadata.create_all(engine)
        ses = sessionmaker(bind=engine)
        session_ob = ses()
        DB.version.Version.make_version(session_ob, engine)
        ses.close_all()
        engine.dispose()

    def get_scoped_session(self):
        return self.sc_session
