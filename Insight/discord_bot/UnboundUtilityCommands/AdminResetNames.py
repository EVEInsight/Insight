from .UnboundCommandBase import *
from sqlalchemy.orm import Session
from database.db_tables import tb_characters, tb_corporations, tb_alliances, tb_types, tb_systems, name_resolver
import InsightExc
import InsightUtilities
from functools import partial


class AdminResetNames(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)
        self.tp = self.unbound.threadpool_unbound

    def command_description(self):
        return "Reset names - Clear and reload all character, corporation, alliance, and type names in the database."

    def __reset_all_names(self)->int:
        reset_count = 0
        db: Session = self.service.get_session()
        try:
            for tabl in [tb_characters, tb_corporations, tb_alliances, tb_types, tb_systems]:
                for row in db.query(tabl).all():
                    row.reset_name()
                    reset_count += 1
                db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.databaseError.DatabaseError
        finally:
            db.close()
            return reset_count

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_index_withAdditional(self.client, d_message)
            options.set_main_header("Here you can reset names or force a download of missing names. You should rarely"
                                    " need to run this, but it is recommended to occasionally run this reset to update"
                                    " names that have been renamed by GMs. Note: Downloading names could take a few"
                                    " minutes and Insight could become unresponsive during the update.")
            options.add_option(dOpt.option_returns_object("Reset and redownload all names.", return_object=0))
            options.add_option(dOpt.option_returns_object("Download missing names only.", return_object=1))
            resp = await options()
            async with InsightUtilities.ThreadPoolPause(self.client.threadpool_insight, timeout=15):
                async with InsightUtilities.ThreadPoolPause(self.client.threadpool_zk, timeout=15):
                    if resp == 0:
                        smsg = "Resetting database names... Insight is temporarily unavailable"
                        self.client.loop.create_task(self.set_status(smsg))
                        reset_count = await self.client.loop.run_in_executor(self.tp, self.__reset_all_names)
                        msg = "{:,} total names were reset.".format(reset_count)
                        self.client.loop.create_task(self.send_status_message(d_message, msg))
                    error_ids = await self.client.loop.run_in_executor(self.tp, partial(name_resolver.api_mass_name_resolve, self.service))
                    missing_count = await self.client.loop.run_in_executor(self.tp, partial(name_resolver.missing_count, self.service))
                    msg = "{} error IDs and a total of {} names still missing from the DB.".format(len(error_ids), missing_count)
                    self.client.loop.create_task(self.send_status_message(d_message, msg))
            if missing_count > 0:
                msg = "A total of {:,} names are still missing from that database. To run another API pull, run the " \
                      "'!admin' command -> Reset names -> Download missing names only.".format(missing_count)
            else:
                msg = "Successfully updated all missing names."
            self.client.loop.create_task(self.send_status_message(d_message, msg))

