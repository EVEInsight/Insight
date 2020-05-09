from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from database.db_tables import tb_kills
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy import func


class KMStats(AbstractEndpoint):
    @staticmethod
    def default_ttl() -> int:
        return 900

    @staticmethod
    def _get_unprefixed_key_hash_sync(last_hours: int):
        return "{}".format(last_hours)

    async def get(self, last_hours: int = 24) -> dict:
        return await super().get(last_hours=last_hours)

    def _do_endpoint_logic_sync(self, last_hours: int) -> dict:
        db = self.db_sessions.get_session()
        start_time = datetime.utcnow() - timedelta(hours=last_hours)
        end_time = datetime.utcnow()
        try:
            stats = db.query(
                func.count(tb_kills.kill_id).label("mailCount"),
                func.sum(tb_kills.totalValue).label("totalValueSum")
            ).filter(
                and_(
                    tb_kills.killmail_time >= start_time,
                    tb_kills.killmail_time <= end_time
                )).one()
        finally:
            db.close()
        return {
            "data": {
                "filters": {
                    "start_time": str(start_time),
                    "end_time": str(end_time)
                },
                "totalKills": stats.mailCount,
                "totalValue": stats.totalValueSum
            }
        }
