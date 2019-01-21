from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.AbyssalLosses import AbyssalLosses


class TestAbyssalFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """without min value set"""
    def need_api_download(self):
        return True

    def download_systems(self):
        return True

    def assert_file_path(self):
        return "Abyssal"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    @property
    def InsightChannelType(self):
        return AbyssalLosses


class TestAbyssalFilter2(TestAbyssalFilter1):
    """with min value set"""
    def get_config_row(self):
        row = super().get_config_row()
        row.minValue = 1000000000
        return row
