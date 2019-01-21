from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.SuperLosses import SuperLosses


class TestSuperLossesFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def populate_group_ids(self):
        yield from [30, 659]

    def assert_file_path(self):
        return "SuperLosses"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    @property
    def InsightChannelType(self):
        return SuperLosses
