from tests.abstract import DatabaseTesting, AsyncTesting
from database.db_tables import tb_kills, tb_groups, tb_constellations, tb_categories, tb_systems, tb_regions
from database.db_tables.discord import tb_channels, tb_enfeed
from database.db_tables.filters import tb_Filter_characters, tb_Filter_corporations, tb_Filter_alliances, tb_Filter_systems
from tests.mocks.libDiscord.TextChannel import TextChannel
from tests.mocks.ServiceModule import ServiceModule
import datetime


class AbstractFilterTesting(DatabaseTesting.DatabaseTesting, AsyncTesting.AsyncTesting):
    def setUp(self):
        AsyncTesting.AsyncTesting.setUp(self)
        self.resources = None
        DatabaseTesting.DatabaseTesting.setUp(self)
        self.set_resource_path("db_tables", "eve", "mails")
        self.assert_files = self.get_resource_path("DiscordBot", "ChannelTypes", "FiltersVisualsEmbedded",
                                                   self.assert_file_path())
        self.service = ServiceModule(self.scoped_session)
        for km_data_id in list(self.filter_pass_ids()) + list(self.filter_fail_ids()):
            data = self.file_json("{}.json".format(km_data_id))
            tb_kills.make_row(data.get("package"), self.service)
        self.db.merge(self.get_config_row())
        for filter_id in self.filter_character_ids():
            self.db.merge(tb_Filter_characters(filter_id, 1, True))
        for filter_id in self.filter_corporation_ids():
            self.db.merge(tb_Filter_corporations(filter_id, 1, True))
        for filter_id in self.filter_alliance_ids():
            self.db.merge(tb_Filter_alliances(filter_id, 1, True))
        for filter_id in self.filter_systems_ids():
            self.db.merge(tb_Filter_systems(filter_id, 1, True))
        for group_id in self.populate_group_ids():
            self.db.merge(tb_groups(group_id))
        for cat_id in self.populate_category_ids():
            self.db.merge(tb_categories(cat_id))
        self.db.commit()
        self.channel = TextChannel(1, 1)
        self.InsightChannel = None
        self.get_channel_object()
        self.loop.run_until_complete(self.InsightChannel.async_load_table())

    def helper_download_data(self):
        tb_groups.api_mass_data_resolve(self.service)
        tb_categories.api_mass_data_resolve(self.service)
        if self.download_systems():
            tb_systems.api_mass_data_resolve(self.service)
        tb_constellations.api_mass_data_resolve(self.service)
        tb_regions.api_mass_data_resolve(self.service)
        self.loop.run_until_complete(self.InsightChannel.async_load_table())

    def get_channel_object(self):
        self.InsightChannel = self.InsightChannelType(self.channel, self.service)
        return self.InsightChannel

    def need_api_download(self):
        return False

    def download_systems(self):
        return False

    def assert_file_path(self):
        raise NotImplementedError
        # 'return "EntityFeed"'

    def get_config_row(self):
        t = self.InsightChannelType.linked_table()
        row: tb_enfeed = t(1)
        row.template_id = self.InsightChannelType.get_template_id()
        return row

    def populate_group_ids(self):
        return
        yield

    def populate_category_ids(self):
        return
        yield

    def filter_character_ids(self):
        return
        yield

    def filter_corporation_ids(self):
        return
        yield

    def filter_alliance_ids(self):
        return
        yield

    def filter_systems_ids(self):
        return
        yield

    def filter_pass_ids(self):
        for f in self.filter_pass_assert_file():
            yield from [int(i) for i in self.get_file_lines_from_abs(self.assert_files, f)]

    def filter_fail_ids(self):
        for f in self.filter_fail_assert_file():
            yield from [int(i) for i in self.get_file_lines_from_abs(self.assert_files, f)]

    def filter_pass_assert_file(self):
        raise NotImplementedError
        # yield "assert_pass_ids.txt"

    def filter_fail_assert_file(self):
        raise NotImplementedError
        # yield "assert_pass_ids.txt"

    def overwrite_time(self)->datetime.datetime:
        return datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    @property
    def InsightChannelType(self):
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
        for km_id in self.filter_pass_ids():
            with self.subTest(km=km_id, passing=True):
                VisualFilter = self.setup_visual(tb_kills.get_row({"killID": km_id}, self.service))
                self.mock_modify_before_filter(VisualFilter)
                self.assertTrue(VisualFilter.run_filter())
        for km_id in self.filter_fail_ids():
            with self.subTest(km=km_id, passing=False):
                VisualFilter = self.setup_visual(tb_kills.get_row({"killID": km_id}, self.service))
                self.mock_modify_before_filter(VisualFilter)
                self.assertFalse(VisualFilter.run_filter())

    def test_generate_view(self):
        for km_id in self.filter_pass_ids():
            for appearance in self.InsightChannel.linked_visual_subc().appearance_options():
                self.InsightChannel.cached_feed_table.appearance_id = appearance.appearance_id()
                with self.subTest(km=km_id, visual=appearance.get_desc()):
                    VisualFilter = self.setup_visual(tb_kills.get_row({"killID": km_id}, self.service))
                    self.mock_modify_before_view(VisualFilter)
                    VisualFilter.generate_view()

    def mock_modify_before_filter(self, filter_object):
        pass

    def mock_modify_before_view(self, filter_object):
        pass

