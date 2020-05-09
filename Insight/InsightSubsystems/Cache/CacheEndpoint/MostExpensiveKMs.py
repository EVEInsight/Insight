from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from database.db_tables import tb_kills
from datetime import datetime, timedelta


class MostExpensiveKMs(AbstractEndpoint):
    @staticmethod
    def default_ttl() -> int:
        return 900

    @staticmethod
    def _get_unprefixed_key_hash_sync(batch_limit: int, last_hours: int):
        return "{}:{}".format(batch_limit, last_hours)

    async def get(self, batch_limit: int = 10, last_hours: int = 24) -> dict:
        return await super().get(batch_limit=batch_limit, last_hours=last_hours)

    def _do_endpoint_logic_sync(self, batch_limit: int, last_hours: int) -> dict:
        db = self.db_sessions.get_session()
        kills = []
        try:
            min_time = datetime.utcnow() - timedelta(hours=last_hours)
            r: list = db.query(tb_kills).filter(tb_kills.killmail_time >= min_time).order_by(tb_kills.totalValue.desc()).limit(batch_limit).all()
            for k in r:
                if isinstance(k, tb_kills):
                    kills.append(k.to_jsonDictionary())
        finally:
            db.close()
        return {
            "data": {
                "filters": {
                    "total": len(kills),
                    "start_hours": last_hours
                },
                "kills": kills
            }
        }
