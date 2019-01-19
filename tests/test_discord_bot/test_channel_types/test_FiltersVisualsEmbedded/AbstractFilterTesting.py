from tests.abstract import DatabaseTesting
from database.db_tables import tb_kills
from database.db_tables.discord import tb_channels
from database.db_tables.filters import tb_Filter_characters, tb_Filter_corporations, tb_Filter_alliances
from tests.mocks.libDiscord.TextChannel import TextChannel
from discord_bot.channel_types.FiltersVisualsEmbedded import FiltersVisualsEmbedded
from tests.mocks.ServiceModule import ServiceModule
import datetime
import unittest


class AbstractFilterTesting(DatabaseTesting.DatabaseTesting):
    def setUp(self):
        super().setUp()
        self.set_resource_path("db_tables", "eve", "mails")
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
        self.db.commit()

    def get_config_row(self):
        raise NotImplementedError
        # row = tb_entity(1)

    def filter_character_ids(self):
        raise NotImplementedError

    def filter_corporation_ids(self):
        raise NotImplementedError

    def filter_alliance_ids(self):
        raise NotImplementedError

    def filter_pass_ids(self):
        raise NotImplementedError

    def filter_fail_ids(self):
        raise NotImplementedError

    def overwrite_time(self)->datetime.datetime:
        return datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    def helper_feed_specific(self, row: tb_channels):
        raise NotImplementedError
        # return row.object_enFeed

    @property
    def InsightChannelType(self):
        raise NotImplementedError
        # return EntityFeed

    @property
    def InsightFilter(self):
        raise NotImplementedError
        # return visual_enfeed

    def setup_visual(self, km_id, visual):
        km: tb_kills = tb_kills.get_row({"killID": km_id}, self.service)
        km.killmail_time = self.overwrite_time()
        channel = TextChannel(1, 1)
        filter_channel = tb_channels.get_row(1, self.service)
        feed_specific = self.helper_feed_specific(filter_channel)
        InsightChannel = self.InsightChannelType()
        VisualFilter: FiltersVisualsEmbedded.base_visual = visual(km, channel, filter_channel, feed_specific, InsightChannel)
        return VisualFilter

    def test_run_filter(self):
        for km_id in self.filter_pass_ids():
            with self.subTest(km=km_id, passing=True):
                VisualFilter = self.setup_visual(km_id, self.InsightFilter)
                self.assertTrue(VisualFilter.run_filter())
        for km_id in self.filter_fail_ids():
            with self.subTest(km=km_id, passing=False):
                VisualFilter = self.setup_visual(km_id, self.InsightFilter)
                self.assertFalse(VisualFilter.run_filter())

    def test_generate_view(self):
        for km_id in self.filter_pass_ids():
            for appearance in self.InsightFilter.appearance_options():
                with self.subTest(km=km_id, visual=appearance.get_desc()):
                    VisualFilter = self.setup_visual(km_id, appearance)
                    VisualFilter.generate_view()
