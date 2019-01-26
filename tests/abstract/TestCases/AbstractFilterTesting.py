from tests.abstract import DatabaseTesting, AsyncTesting
from database.db_tables import tb_kills, tb_groups, tb_constellations, tb_categories, tb_systems, tb_regions
from database.db_tables.discord import tb_channels, tb_enfeed
from database.db_tables.filters import tb_Filter_characters, tb_Filter_corporations, tb_Filter_alliances, tb_Filter_systems
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.ServiceModule import ServiceModule
import datetime
from  sqlalchemy.sql.expression import func


class AbstractFilterTesting(DatabaseTesting.DatabaseTesting, AsyncTesting.AsyncTesting):
    @classmethod
    def setUpClass(cls):
        path_mails = cls.get_resource_path("database", "db_tables", "eve", "mails")
        cls.assert_files = cls.get_resource_path("DiscordBot", "ChannelTypes", "FiltersVisualsEmbedded",
                                                   cls.assert_file_path())
        cls.engine = cls.get_engine()
        cls.scoped_session = cls.get_scoped_session(cls.engine)
        cls.db = cls.get_session(cls.engine)
        cls.service = ServiceModule(cls.scoped_session)
        for km_data_id in list(cls.filter_pass_ids()) + list(cls.filter_fail_ids()):
            data = cls.file_json_from_abs(path_mails, "{}.json".format(km_data_id))
            tb_kills.make_row(data.get("package"), cls.service)
        cls.db.merge(cls.get_config_row())
        for filter_id in cls.filter_character_ids():
            cls.db.merge(tb_Filter_characters(filter_id, 1, True))
        for filter_id in cls.filter_corporation_ids():
            cls.db.merge(tb_Filter_corporations(filter_id, 1, True))
        for filter_id in cls.filter_alliance_ids():
            cls.db.merge(tb_Filter_alliances(filter_id, 1, True))
        for filter_id in cls.filter_systems_ids():
            cls.db.merge(tb_Filter_systems(filter_id, 1, True))
        for group_id in cls.populate_group_ids():
            cls.db.merge(tb_groups(group_id))
        for cat_id in cls.populate_category_ids():
            cls.db.merge(tb_categories(cat_id))
        cls.db.commit()
        cls.db.close()

    @classmethod
    def tearDownClass(cls):
        cls.metadata_drop_all(cls.engine)

    def setUp(self):
        AsyncTesting.AsyncTesting.setUp(self)
        self.channel = TextChannel(1, 1)
        self.InsightChannel = None
        self.get_channel_object()
        self.loop.run_until_complete(self.InsightChannel.async_load_table())

    def tearDown(self):
        AsyncTesting.AsyncTesting.tearDown(self)

    def helper_download_data(self):
        tb_groups.api_mass_data_resolve(self.service)
        tb_categories.api_mass_data_resolve(self.service)
        if self.download_systems():
            tb_systems.api_mass_data_resolve(self.service)
        tb_constellations.api_mass_data_resolve(self.service)
        tb_regions.api_mass_data_resolve(self.service)
        self.loop.run_until_complete(self.InsightChannel.async_load_table())

    def get_channel_object(self):
        self.InsightChannel = self.InsightChannelType()(self.channel, self.service)
        return self.InsightChannel

    def need_api_download(self):
        return False

    def download_systems(self):
        return False

    @classmethod
    def assert_file_path(cls):
        raise NotImplementedError
        # 'return "EntityFeed"'

    @classmethod
    def get_config_row(cls):
        t = cls.InsightChannelType().linked_table()
        row: tb_enfeed = t(1)
        row.template_id = cls.InsightChannelType().get_template_id()
        return row

    @classmethod
    def populate_group_ids(cls):
        return
        yield

    @classmethod
    def populate_category_ids(cls):
        return
        yield

    @classmethod
    def filter_character_ids(cls):
        return
        yield

    @classmethod
    def filter_corporation_ids(cls):
        return
        yield

    @classmethod
    def filter_alliance_ids(cls):
        return
        yield

    @classmethod
    def filter_systems_ids(cls):
        return
        yield

    @classmethod
    def filter_pass_ids(cls):
        for f in cls.filter_pass_assert_file():
            yield from [int(i) for i in cls.get_file_lines_from_abs(cls.assert_files, f)]

    @classmethod
    def filter_fail_ids(cls):
        for f in cls.filter_fail_assert_file():
            yield from [int(i) for i in cls.get_file_lines_from_abs(cls.assert_files, f)]

    @classmethod
    def filter_pass_assert_file(cls):
        raise NotImplementedError
        # yield "assert_pass_ids.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        raise NotImplementedError
        # yield "assert_pass_ids.txt"

    def overwrite_time(self)->datetime.datetime:
        return datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    @classmethod
    def InsightChannelType(cls):
        raise NotImplementedError
        # return EntityFeed

    def setup_visual(self, km_object):
        km_object.killmail_time = self.overwrite_time()
        visual = self.InsightChannel.linked_visual_subc()
        return visual(km_object, self.channel, self.InsightChannel.cached_feed_table,
                      self.InsightChannel.cached_feed_specific, self.InsightChannel)

    def test_run_filter(self):
        if self.need_api_download():
            self.helper_download_data()
            self.get_channel_object()
        pass_ids = set(self.filter_pass_ids())
        fail_ids = set(self.filter_fail_ids())
        for km in self.db.query(tb_kills).all():
            if km.kill_id in pass_ids:
                with self.subTest(km=km.kill_id, passing=True):
                    VisualFilter = self.setup_visual(km)
                    self.mock_modify_before_filter(VisualFilter)
                    self.assertTrue(VisualFilter.run_filter())
            elif km.kill_id in fail_ids:
                with self.subTest(km=km.kill_id, passing=False):
                    VisualFilter = self.setup_visual(km)
                    self.mock_modify_before_filter(VisualFilter)
                    self.assertFalse(VisualFilter.run_filter())

    def test_generate_view(self):
        for km in self.db.query(tb_kills).order_by(func.random()).limit(25).all():
            for appearance in self.InsightChannel.linked_visual_subc().appearance_options():
                self.InsightChannel.cached_feed_table.appearance_id = appearance.appearance_id()
                with self.subTest(km=km.kill_id, visual=appearance.get_desc()):
                    VisualFilter = self.setup_visual(km)
                    self.mock_modify_before_view(VisualFilter)
                    VisualFilter.generate_view()

    def mock_modify_before_filter(self, filter_object):
        pass

    def mock_modify_before_view(self, filter_object):
        pass

