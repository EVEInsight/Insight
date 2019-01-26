from tests.abstract import DatabaseTesting
from tests.mocks import ServiceModule

class AbstractTestBase(DatabaseTesting.DatabaseTesting):
    @property
    def helper_assert_name(self):
        raise NotImplementedError
        # return "Northern Coalition."

    @property
    def helper_assert_id(self):
        raise NotImplementedError
        # return 1727758877

    @property
    def helper_row(self):
        raise NotImplementedError
        # return tb_alliances

    @property
    def helper_pk(self):
        raise NotImplementedError
        # return tb_alliances.alliance_id

    @property
    def helper_assert_api_category(self):
        raise NotImplementedError
        # return UniverseApi

    def setUp(self):
        super().setUp()
        self.service = ServiceModule.ServiceModule(self.db)
        self.db.add(self.helper_row(self.helper_assert_id))
        self.db.commit()

    def helper_get_row(self, item_id):
        return self.db.query(self.helper_row).filter(self.helper_pk == item_id).one()
