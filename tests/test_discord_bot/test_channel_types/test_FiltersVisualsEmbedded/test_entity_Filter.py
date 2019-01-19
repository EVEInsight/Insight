from tests.test_discord_bot.test_channel_types.test_FiltersVisualsEmbedded import AbstractFilterTesting
from database.db_tables.discord import tb_channels, tb_enfeed, enum_kmType
from tests.mocks.InsightBot.EntityFeed import EntityFeed
from discord_bot.channel_types.FiltersVisualsEmbedded import visual_enfeed


class TestEntityFilter(AbstractFilterTesting.AbstractFilterTesting):
    def get_config_row(self):
        row = tb_enfeed(1)
        row.show_mode = enum_kmType.show_both
        return row

    def filter_character_ids(self):
        return
        yield

    def filter_corporation_ids(self):
        return
        yield

    def filter_alliance_ids(self):
        yield 99005338

    def filter_pass_ids(self):
        yield 74647898

    def filter_fail_ids(self):
        yield 74647835

    def helper_feed_specific(self, row: tb_channels):
        return row.object_enFeed

    @property
    def InsightChannelType(self):
        return EntityFeed

    @property
    def InsightFilter(self):
        return visual_enfeed

