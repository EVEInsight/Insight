from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from sqlalchemy import func
from database.db_tables import tb_characters, tb_corporations, tb_alliances

class NamesDoomheim(AbstractCronTask):
    def call_now(self) -> bool:
        return False

    def run_at_intervals(self) -> bool:
        return False

    def loop_iteration(self) -> int:
        return 900

    def _rename_duplicates(self, table_column_name, table_column_id, table):
        db = self.service.get_session()
        try:
            duplicate_names = db.query(table_column_name).filter(table_column_name != None).group_by(table_column_name).having(func.count(table_column_name) > 1).all()
            if len(duplicate_names) > 0:
                for n in duplicate_names:
                    name = n[0]
                    update_objects = db.query(table).filter(table_column_name == name).order_by(table_column_id.desc()).all()
                    row_iteration = 0
                    for row in update_objects:
                        row_iteration += 1
                        if row_iteration == 1:
                            continue
                        else:
                            if isinstance(row, tb_characters):
                                row.set_name("{} (!Doomheim!)".format(name))
                            else:
                                row.set_name("{} (!Closed!)".format(name))
                db.commit()
        finally:
            db.close()

    def _rename_duplicate_chars(self):
        self._rename_duplicates(tb_characters.character_name, tb_characters.character_id, tb_characters)
        self._rename_duplicates(tb_corporations.corporation_name, tb_corporations.corporation_id, tb_corporations)
        self._rename_duplicates(tb_alliances.alliance_name, tb_alliances.alliance_name, tb_alliances)

    async def _run_task(self):
        await self.loop.run_in_executor(None, self._rename_duplicate_chars)
