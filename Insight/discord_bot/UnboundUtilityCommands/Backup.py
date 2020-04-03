from .UnboundCommandBase import *
import InsightUtilities
import shutil
import os
import datetime


class Backup(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.cLock = asyncio.Lock(loop=self.client.loop)
        self.tp = self.unbound.threadpool_unbound

    def command_description(self):
        return "Backup - Backup the current Insight database and all logs into a zip archive."

    def run_backup(self):
        try:
            backup_name = datetime.datetime.utcnow().strftime('%m_%d_%Y_%H_%M') + '-backup'
            backup_path = os.path.join('backups', backup_name)
            shutil.copytree('logs', os.path.join(backup_path, 'logs'))
            shutil.copy2(self.service.config.get("SQLITE_DB_PATH"), backup_path)
            shutil.make_archive(os.path.join('backups', backup_name), 'zip', backup_path)
            shutil.rmtree(backup_path)
            return "Successfully backed up the Insight database to {}.zip".format(backup_path)
        except Exception as ex:
            print(ex)
            return "Error when backing up the database: {}".format(ex)

    async def run_command(self, d_message: discord.Message, m_text: str = ""):
        async with self.cLock:
            options = dOpt.mapper_return_yes_no(self.client, d_message)
            options.set_main_header("Are you sure you want to initiate an Insight backup? Note: Insight will be "
                                    "unresponsive and unavailable for the duration of the backup.")
            resp = await options()
            if resp:
                async with InsightUtilities.ThreadPoolPause(self.client.threadpool_insight, timeout=15):
                    async with InsightUtilities.ThreadPoolPause(self.client.threadpool_zk, timeout=15):
                        self.client.loop.create_task(self.set_status('Backup in progress... Insight is temporarily unavailable'))
                        resp = await self.client.loop.run_in_executor(self.tp, self.run_backup)
                        self.client.loop.create_task(self.send_status_message(d_message, resp))
