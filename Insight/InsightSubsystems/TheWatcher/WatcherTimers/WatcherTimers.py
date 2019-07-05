from InsightSubsystems.TheWatcher import TheWatcher
from InsightSubsystems.TheWatcher.WatcherTasks import LoadEntireDB
from database.db_tables import tb_meta
import asyncio
import InsightLogger
import datetime


class WatcherTimers(object):
    def __init__(self, watcher_main):
        self.watcher: TheWatcher.TheWatcher = watcher_main
        self.service = self.watcher.service
        self.config_load_all = self.service.config_file.getboolean("TheWatcher", "load_all", fallback=False)
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.cron", "Watcher_cron.log", console_print=True)
        self.task_lock = asyncio.Lock(loop=self.watcher.loop)

        self.loop_load_all_timer = 3600
        self.loop_save_states_timer = 900

    async def task_load_all(self):
        self.logger.info("Starting the load_all task.")
        if not self.config_load_all:
            self.logger.info("This task has been blocked by the TheWatcher.load_all config flag in the config file.")
            return
        next_run = await self.watcher.executor(tb_meta.get_last_full_pull, self.service) + datetime.timedelta(days=15)
        if datetime.datetime.utcnow() < next_run:
            self.logger.info("This task will run after it is: {}. Exiting.".format(next_run))
            return
        await self.watcher.reset_all()
        self.logger.info("Cleared all current data.")
        task = LoadEntireDB.LoadEntireDB(self.watcher)
        await task.run_task()

    async def timer_load_all(self):
        """this task will load all mails from the database"""
        while True:
            async with self.task_lock:
                try:
                    await self.task_load_all()
                except:
                    self.logger.exception("task_load_all")
                await asyncio.sleep(self.loop_load_all_timer)

    async def timer_save_states(self):
        """this task will load all mails from the database"""
        while True:
            async with self.task_lock:
                try:
                    pass
                except:
                    self.logger.exception("task_save_states")
                await asyncio.sleep(self.loop_save_states_timer)

    async def start_tasks(self):
        self.watcher.loop.create_task(self.timer_load_all())
        self.watcher.loop.create_task(self.timer_save_states())
