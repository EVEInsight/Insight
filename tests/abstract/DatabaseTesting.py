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

    def assert_contains(self, results, row_type, row_pk_id):
        for r in results:
            if isinstance(r, row_type) and r.get_id() == row_pk_id:
                return
        self.fail("Missing item with id: {} and type: {}".format(row_pk_id, str(row_type)))

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
        with open(os.path.join(cls.sql_root, file), 'r', encoding='utf-8') as f:
            for statement in f:
                engine.execute(statement)

    @classmethod
    def import_systems(cls, engine, full_data=False):
        cls._sql_import("systems.sql" if not full_data else "systems_full.sql", engine)

    @classmethod
    def import_stargates(cls, engine, full_data=False):
        cls._sql_import("stargates.sql", engine)

    @classmethod
    def import_types(cls, engine, full_data=False):
        cls._sql_import("types.sql" if not full_data else "types_full.sql", engine)

    @classmethod
    def import_groups(cls, engine, full_data=False):
        cls._sql_import("groups.sql" if not full_data else "groups_full.sql", engine)

    @classmethod
    def import_type_group_category(cls, engine, full_data=False):
        cls._sql_import("categories.sql", engine)  # todo account for full eventually
        cls.import_groups(engine, full_data)
        cls.import_types(engine, full_data)

    @classmethod
    def import_system_constellation_region(cls, engine, full_data=False):
        cls._sql_import("regions.sql" if not full_data else "regions_full.sql", engine)
        cls._sql_import("constellations.sql" if not full_data else "constellations_full.sql", engine)
        cls.import_systems(engine, full_data)
