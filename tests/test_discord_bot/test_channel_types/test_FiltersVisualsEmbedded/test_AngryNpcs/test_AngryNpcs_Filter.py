from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.AngryNPC import AngryNPC


class TestAngryNpcsFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """no minimum value set"""
    @classmethod
    def import_item_db(cls):
        return True

    @classmethod
    def assert_file_path(cls):
        return "AngryNpcs"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def InsightChannelType(cls):
        return AngryNPC


class TestAngryNpcsFilter2(TestAngryNpcsFilter1):
    """min value set"""
    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.minValue = 5000000000
        return row

    @classmethod
    def filter_pass_assert_file(cls):
        yield "2_pass.txt"
