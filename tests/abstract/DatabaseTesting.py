from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from tests.mocks import ServiceModule, DiscordInsightClient
from database.db_tables import Base
from tests.abstract import InsightTestBase
from sqlalchemy.pool import StaticPool


class DatabaseTesting(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.set_resource_path('database')
        self.engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
        self.scoped_session = sessionmaker(bind=self.engine)
        self.db = Session(self.engine)
        Base.Base.metadata.create_all(self.engine)
        self.service = ServiceModule.ServiceModule(self.db)
        self.client = DiscordInsightClient.DiscordInsightClient()

    def tearDown(self):
        Base.Base.metadata.drop_all(self.engine)
