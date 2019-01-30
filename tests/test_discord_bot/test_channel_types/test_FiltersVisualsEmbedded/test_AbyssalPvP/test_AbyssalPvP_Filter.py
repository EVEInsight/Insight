from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.AbyssalPvP import AbyssalPvP


class TestAbyssalPvPFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """without min value set"""
    @classmethod
    def import_map_db(cls):
        return True

    @classmethod
    def assert_file_path(cls):
        return "AbyssalPvP"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def InsightChannelType(cls):
        return AbyssalPvP
