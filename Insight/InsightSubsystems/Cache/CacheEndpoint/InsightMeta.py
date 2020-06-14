from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from database.db_tables import tb_meta
from InsightUtilities.StaticHelpers import Helpers
from dateutil.parser import parse as dateTimeParser
from datetime import datetime


class InsightMeta(AbstractEndpoint):
    @staticmethod
    def default_ttl() -> int:
        return 900  # 15 minutes

    @staticmethod
    def _get_unprefixed_key_hash_sync(meta_key: str):
        return "{}".format(meta_key)

    async def get(self, meta_key: str) -> dict:
        return await super().get(meta_key=meta_key)

    async def delete_no_fail(self, meta_key: str):
        return await super().delete_no_fail(meta_key=meta_key)

    def sync_process_before_return(self, data_dict: dict) -> dict:
        modified_time = Helpers.get_nested_value(data_dict, datetime.utcnow(), "data", "modified")
        if isinstance(modified_time, str):
            data_dict["data"]["modified"] = dateTimeParser(modified_time)
        access_time = Helpers.get_nested_value(data_dict, datetime.utcnow(), "data", "access")
        if isinstance(access_time, str):
            data_dict["data"]["access"] = dateTimeParser(access_time)
        return data_dict

    def _do_endpoint_logic_sync(self, meta_key) -> dict:
        row = tb_meta.get(meta_key)
        return_dict = {"data": {
            "key": Helpers.get_nested_value(row, meta_key, "key"),
            "data": Helpers.get_nested_value(row, {}, "data"),
            "modified": str(Helpers.get_nested_value(row, {}, "modified")),
            "access": str(Helpers.get_nested_value(row, {}, "access"))}
        }
        return return_dict
