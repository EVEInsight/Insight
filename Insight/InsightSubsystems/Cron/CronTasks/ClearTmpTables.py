from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from database.db_tables import tb_temp_intjoin, tb_temp_strjoin
import time

class ClearTmpTables(AbstractCronTask):
    def call_now(self) -> bool:
        return False

    def run_at_intervals(self) -> bool:
        return False

    def loop_iteration(self) -> int:
        return 1800

    def _clear_tmp_tables(self):
        db = self.service.get_session()
        try:
            epoch = int(time.time()) - 900
            for r in db.query(tb_temp_intjoin).filter(tb_temp_intjoin.epoch <= epoch).all():
                db.delete(r)
            for r in db.query(tb_temp_strjoin).filter(tb_temp_strjoin.epoch <= epoch).all():
                db.delete(r)
            db.commit()
        finally:
            db.close()

    async def _run_task(self):
        await self.loop.run_in_executor(None, self._clear_tmp_tables)
