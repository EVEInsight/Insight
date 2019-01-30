from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from tests.mocks import ServiceModule, DiscordInsightClient
from database.db_tables import Base
from tests.abstract import InsightTestBase
from sqlalchemy.pool import StaticPool
import sqlalchemy
import os


class DatabaseTesting(InsightTestBase.InsightTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sql_root = cls.get_resource_path("database", "sql", path=None)

    def setUp(self):
        super().setUp()
        self.set_resource_path('database')
        self.engine = self.get_engine()
        self.scoped_session = self.get_scoped_session(self.engine)
        self.db = self.get_session(self.engine)
        self.service = ServiceModule.ServiceModule(self.scoped_session)
        self.client = DiscordInsightClient.DiscordInsightClient()

    def tearDown(self):
        super().tearDown()
        self.db.close()
        self.scoped_session.remove()
        self.metadata_drop_all(self.engine)

    @classmethod
    def get_engine(cls):
        engine = create_engine('sqlite:///', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        cls._metadata_create_all(engine)
        return engine

    @classmethod
    def get_scoped_session(cls, engine):
        return scoped_session(sessionmaker(bind=engine))

    @classmethod
    def get_session(cls, engine):
        return Session(engine)

    @classmethod
    def _metadata_create_all(cls, engine):
        Base.Base.metadata.create_all(engine)

    @classmethod
    def metadata_drop_all(cls, engine):
        Base.Base.metadata.drop_all(engine)

    @classmethod
    def _sql_import(cls, file, engine):
        with open(os.path.join(cls.sql_root, file), 'r') as f:
            for statement in f:
                engine.execute(statement)

    @classmethod
    def import_systems(cls, engine):
        cls._sql_import("systems.sql", engine)

    @classmethod
    def import_stargates(cls, engine):
        cls._sql_import("stargates.sql", engine)

    @classmethod
    def import_type_group_category(cls, engine):
        cls._sql_import("categories.sql", engine)
        cls._sql_import("groups.sql", engine)
        cls._sql_import("types.sql", engine)

    @classmethod
    def import_system_constellation_region(cls, engine):
        cls._sql_import("regions.sql", engine)
        cls._sql_import("constellations.sql", engine)
        cls._sql_import("systems.sql", engine)
