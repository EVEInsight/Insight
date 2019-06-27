from tests.abstract.TestCases import AbstractFilterTesting
from discord_bot.channel_types.TemplateFeeds.ShipLosses import ShipLosses
from database.db_tables import tb_enfeed, tb_Filter_types, tb_Filter_groups


class TestShipLossesFilter1(AbstractFilterTesting.AbstractFilterTesting):
    """whitelist drakes, rifters, and battleships between 150 and 400m"""
    @classmethod
    def import_item_db(cls):
        return True

    @classmethod
    def get_config_row(cls):
        row: tb_enfeed = super().get_config_row()
        row.minValue = 150000000
        row.maxValue = 400000000
        return row

    @classmethod
    def filter_group_ids(cls):
        yield 27

    @classmethod
    def filter_type_ids(cls):
        yield 24698
        yield 587

    @classmethod
    def assert_file_path(cls):
        return "ShipLosses"

    @classmethod
    def filter_pass_assert_file(cls):
        yield "1_pass.txt"

    @classmethod
    def filter_fail_assert_file(cls):
        yield "superlosses_1_pass.txt"

    @classmethod
    def InsightChannelType(cls):
        return ShipLosses
