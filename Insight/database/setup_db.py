from sqlalchemy.orm import scoped_session, sessionmaker,Session
from sqlalchemy import create_engine
import database.db_tables as DB
import sys


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
        self.verify_tokens()

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

    def verify_tokens(self):
        try:
            db: Session = self.sc_session()
            tokens = db.query(tb_tokens).all()
            db.close()
        except:
            print("The token table is corrupted. If you modified your database encryption secret key located in your "
                  "config file all existing tokens become invalid. Insight will not work until this issue is resolved. "
                  "You must either restore your previous encryption key or delete all existing tokens.")
            resp = input(
                "\n\nReset all tokens? Note: You will be unable to use Insight until this error goes away. "
                "[Y/n]: ").lower()
            if resp.startswith('y'):
                tb_contacts_alliances.__table__.drop(self.engine)
                tb_contacts_corps.__table__.drop(self.engine)
                tb_contacts_pilots.__table__.drop(self.engine)
                tb_discord_tokens.__table__.drop(self.engine)
                tb_tokens.__table__.drop(self.engine)
                self.service.read_config_file(self.service.cli_args.config, newkey=True)
                print("Issue resolved. You must restart Insight.")
                sys.exit(0)
            elif resp.startswith('n'):
                print("No changes you were made. You must resolve this issue before starting Insight.")
                sys.exit(1)
            else:
                print("Unknown response. No changes were made.")
                sys.exit(1)


from .db_tables import tb_contacts_alliances, tb_contacts_corps, tb_contacts_pilots, tb_tokens, tb_discord_tokens
