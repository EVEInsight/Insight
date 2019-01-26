from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.AbyssalLosses import AbyssalLosses


class TestAbyssalFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """without min value set"""
    def need_api_download(self):
        return True

    @classmethod
    def download_systems(cls):
        return True

    @classmethod
    def assert_file_path(cls):
        return "Abyssal"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def InsightChannelType(cls):
        return AbyssalLosses


class TestAbyssalFilter2(TestAbyssalFilter1):
    """with min value set"""
    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.minValue = 1000000000
        return row
