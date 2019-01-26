from tests.abstract.TestCases import AbstractFilterTesting
from database.db_tables.discord import enum_kmType
from discord_bot.channel_types.enFeed import enFeed


class TestEntityFilterKillsOnly1(AbstractFilterTesting.AbstractFilterTesting):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""
    @classmethod
    def assert_file_path(cls):
        return "EntityFeed"

    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.show_mode = enum_kmType.kills_only
        return row

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "1_fail.txt"

    @classmethod
    def filter_character_ids(cls):
        yield 317012339

    @classmethod
    def filter_corporation_ids(cls):
        yield 1431056470

    @classmethod
    def filter_alliance_ids(cls):
        yield 1727758877
        yield 498125261

    @classmethod
    def InsightChannelType(cls):
        return enFeed


class TestEntityFilterLossOnly2(TestEntityFilterKillsOnly1):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""

    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.show_mode = enum_kmType.losses_only
        return row

    @classmethod
    def filter_pass_assert_file(cls):
        yield "2_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "2_fail.txt"


class TestEntityFilterBoth3(TestEntityFilterKillsOnly1):
    """Test case for entity feed configured with tracked pilot, corp, and alliances. Set to show kills only"""

    @classmethod
    def get_config_row(cls):
        row = super().get_config_row()
        row.show_mode = enum_kmType.show_both
        return row

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"
        yield "2_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "3_fail.txt"
