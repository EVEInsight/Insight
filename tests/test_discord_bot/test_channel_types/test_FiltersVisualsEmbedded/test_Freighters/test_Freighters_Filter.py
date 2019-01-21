from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.Freighters import Freighters


class TestFreightersFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def download_systems(self):
        return True

    def populate_group_ids(self):
        yield from [513, 902]

    def assert_file_path(self):
        return "Freighters"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    @property
    def InsightChannelType(self):
        return Freighters
