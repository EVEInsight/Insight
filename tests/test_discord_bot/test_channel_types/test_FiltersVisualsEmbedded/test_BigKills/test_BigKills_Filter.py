from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.BigKills import BigKills


class TestBigKillsFilter1(AbstractFilterTesting.AbstractFilterTesting):
    def need_api_download(self):
        return True

    def get_config_row(self):
        row = super().get_config_row()
        row.minValue = 15000000000
        return row

    def assert_file_path(self):
        return "BigKills"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"
        yield "superlosses_1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    @property
    def InsightChannelType(self):
        return BigKills
