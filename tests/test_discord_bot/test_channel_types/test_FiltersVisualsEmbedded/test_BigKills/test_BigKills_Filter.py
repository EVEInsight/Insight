from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.BigKills import BigKills


class TestBigKillsFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.minValue = 15000000000
        return row

    @classmethod
    def assert_file_path(cls):
        return "BigKills"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"
        yield "superlosses_1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def InsightChannelType(cls):
        return BigKills
