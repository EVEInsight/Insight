from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.AngryNPC import AngryNPC


class TestAngryNpcsFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """no minimum value set"""
    def assert_file_path(self):
        return "AngryNpcs"

    def filter_pass_assert_file(self):
        yield "1_pass.txt"

    def filter_fail_assert_file(self):
        yield "1_fail.txt"

    @property
    def InsightChannelType(self):
        return AngryNPC


class TestAngryNpcsFilter2(TestAngryNpcsFilter1):
    """min value set"""
    def get_config_row(self):
        row = super().get_config_row()
        row.minValue = 5000000000
        return row

    def filter_pass_assert_file(self):
        yield "2_pass.txt"
