from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.Freighters import Freighters


class TestFreightersFilter1(AbstractFilterTesting.AbstractFilterTesting):
    @classmethod
    def import_item_db(cls):
        return True

    @classmethod
    def import_map_db(cls):
        return True

    @classmethod
    def assert_file_path(cls):
        return "Freighters"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def InsightChannelType(cls):
        return Freighters
