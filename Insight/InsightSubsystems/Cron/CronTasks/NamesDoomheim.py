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

    def _sort_ids(self, row_list):
        """sort ids for custom sort defined here to find the most recently created entity https://docs.esi.evetech.net/docs/id_ranges.html"""
        return_list = []
        for row in row_list:
            if isinstance(row, tb_corporations) or isinstance(row, tb_alliances):
                after_nov2010 = []
                before_nov2010 = []
                if int(100e6) <= row.get_id() < int(21e8): # 100,000,000 <= id < 2,100,000,000
                    before_nov2010.append(row)
                else: # 98,000,000 <= id < 100,000,000
                    after_nov2010.append(row)
                return_list += after_nov2010
                return_list += before_nov2010
            else: #characters
                after_may2016 = []
                nov2010_to_may2016 = []
                before_nov2010 = []
                if int(90e6) <= row.get_id() < int(98e6): # 90,000,000 <= id < 98,000,000
                    nov2010_to_may2016.append(row)
                elif int(100e6) <= row.get_id() < int(21e8): # 100,000,000 <= id < 2,100,000,000
                    before_nov2010.append(row)
                else: #2,100,000,000 to 2,147,483,647
                    after_may2016.append(row)
                return_list += after_may2016
                return_list += nov2010_to_may2016
                return_list += before_nov2010
        return return_list

    def _rename_duplicates(self, table_column_name, table_column_id, table):
        db = self.service.get_session()
        try:
            if db.query(table).filter(table_column_name == None).count() > 0:
                self.lg.warning("Skipping rename duplicates on table: {} as not all names are currently resolved".format(str(table.__name__)))
                return
            duplicate_names = db.query(table_column_name).filter(table_column_name != None).group_by(table_column_name).having(func.count(table_column_name) > 1).all()
            if len(duplicate_names) > 0:
                for n in duplicate_names:
                    name = n[0]
                    if "(!Doomheim!)" in name or "(!Closed!)" in name:
                        continue
                    update_objects = self._sort_ids(db.query(table).filter(table_column_name == name).order_by(table_column_id.desc()).all())
                    row_iteration = 0
                    for row in update_objects:
                        row_iteration += 1
                        if row_iteration == 1:
                            self.lg.info("Found {} duplicates of name '{}'. ID of open / top entity is {}.".format(len(update_objects), row.get_name(), row.get_id()))
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
        self._rename_duplicates(tb_alliances.alliance_name, tb_alliances.alliance_id, tb_alliances)

    async def _run_task(self):
        await self.loop.run_in_executor(None, self._rename_duplicate_chars)
