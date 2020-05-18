from sqlalchemy.orm import scoped_session, sessionmaker,Session
from sqlalchemy import create_engine
import database.db_tables as DB
import sys
from InsightUtilities import ColumnEncryption


class setup_database(object):
    sc_session: scoped_session

    def __init__(self, service_module):
        self.service = service_module
        self.using_postgres = False
        if self.service.config.get("DB_DRIVER") == "postgres":
            self.using_postgres = True
            self.connection_str = "postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}".format(
                user=self.service.config.get("POSTGRES_USER"), pw=self.service.config.get("POSTGRES_PASSWORD"),
                host=self.service.config.get("POSTGRES_HOST"), port=self.service.config.get("POSTGRES_PORT"),
                db=self.service.config.get("POSTGRES_DB"))
        elif self.service.config.get("DB_DRIVER") == "sqlite3":
            self.connection_str = "sqlite:///{}".format(self.service.config.get("SQLITE_DB_PATH"))
        else:
            print("Invalid value: '{}' for DB_DRIVER. Must be either 'postgres' or 'sqlite3'.\n".
                  format(self.service.config.get("DB_DRIVER")))
            sys.exit(1)
        self.initial_load()
        if self.using_postgres:
            self.engine = create_engine(self.connection_str, echo=False,
                                        pool_size=self.service.config.get("POSTGRES_POOLSIZE"),
                                        max_overflow=self.service.config.get("POSTGRES_POOLOVERFLOW"),
                                        pool_pre_ping=True)
        else:
            self.engine = create_engine(self.connection_str, connect_args={'check_same_thread': False, 'timeout': 3000},
                                        echo=False)
        DB.Base.Base.metadata.create_all(self.engine)
        self._dbSession = sessionmaker(bind=self.engine)
        self.sc_session = scoped_session(self._dbSession)
        self.verify_tokens()

    def initial_load(self):
        if self.using_postgres:
            engine = create_engine(self.connection_str, echo=False)
        else:
            engine = create_engine(self.connection_str, connect_args={'check_same_thread': True, 'timeout': 3000},
                                   echo=False)
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
            with open(0) as i:
                sys.stdin = i
                resp = input(
                    "\n\nReset all tokens? Note: You will be unable to use Insight until this error goes away. "
                    "[Y/n]: ").lower()
            if resp.startswith('y'):
                tb_contacts_alliances.__table__.drop(self.engine)
                tb_contacts_corps.__table__.drop(self.engine)
                tb_contacts_pilots.__table__.drop(self.engine)
                tb_discord_tokens.__table__.drop(self.engine)
                tb_tokens.__table__.drop(self.engine)
                ColumnEncryption().reset_key()
                print("Issue resolved. You must restart Insight.")
                sys.exit(0)
            elif resp.startswith('n'):
                print("No changes you were made. You must resolve this issue before starting Insight.")
                sys.exit(1)
            else:
                print("Unknown response. No changes were made.")
                sys.exit(1)

    def shutdown(self):
        try:
            self._dbSession.close_all()
            self.engine.dispose()
            print('Successfully closed the database connections.')
        except Exception as ex:
            print('Error when closing database: {}'.format(ex))


from .db_tables import tb_contacts_alliances, tb_contacts_corps, tb_contacts_pilots, tb_tokens, tb_discord_tokens
