from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tests.mocks import ServiceModule
from database.db_tables import Base
from tests.abstract import InsightTestBase


class DatabaseTesting(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.set_resource_path('database')
        self.engine = create_engine('sqlite:///:memory:')
        self.db = Session(self.engine)
        Base.Base.metadata.create_all(self.engine)
        self.service = ServiceModule.ServiceModule(self.db)

    def tearDown(self):
        Base.Base.metadata.drop_all(self.engine)
