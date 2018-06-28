from sqlalchemy.orm import scoped_session, sessionmaker,Session
from sqlalchemy import create_engine
import database.db_tables as DB


class setup_database(object):
    sc_session: scoped_session

    def __init__(self, service_module):
        self.engine = create_engine('sqlite:///{}'.format(service_module.config_file['sqlite_database']['filename']),
                                    connect_args={'check_same_thread':False,'timeout':3000}, echo=False)
        self.create_tables()
        Session = sessionmaker(bind=self.engine)
        self.sc_session = scoped_session(Session)

    def create_tables(self):
        DB.Base.Base.metadata.create_all(self.engine)

    def get_scoped_session(self):
        return self.sc_session

    @staticmethod
    def test():
        pass


if __name__ == "__main__":
    setup_database.test()