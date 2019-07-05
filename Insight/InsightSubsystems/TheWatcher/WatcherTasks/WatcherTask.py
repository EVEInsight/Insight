from InsightSubsystems.TheWatcher import TheWatcher
import InsightLogger


class WatcherTask(object):
    def __init__(self, watcher_main):
        self.watcher: TheWatcher.TheWatcher = watcher_main
        self.service = self.watcher.service
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.tasks.{}".format(self.__class__.__name__),
                                                             "Watcher_tasks.log")

    def _run_task(self):
        raise NotImplementedError

    async def run_task(self):
        return await self.watcher.executor(self._run_task)
