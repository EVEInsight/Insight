from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.Freighters import Freighters


class TestFreightersFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def download_systems(self):
        return True

    @classmethod
    def populate_group_ids(cls):
        yield from [513, 902]

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
