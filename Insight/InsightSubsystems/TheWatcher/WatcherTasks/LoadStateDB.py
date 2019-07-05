from InsightSubsystems.TheWatcher.WatcherTasks import WatcherTask


class LoadStateDB(WatcherTask.WatcherTask):
    def __init__(self, watcher_main):
        super().__init__(watcher_main)
