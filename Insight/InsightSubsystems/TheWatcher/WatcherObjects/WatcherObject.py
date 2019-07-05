from InsightSubsystems.TheWatcher import TheWatcher
import InsightLogger


class WatcherObject(object):
    def __init__(self, watcher_service):
        self.watcher: TheWatcher.TheWatcher = watcher_service

    def index_check(self):
        raise NotImplementedError

    def id(self):
        raise NotImplementedError

    def name(self):
        raise NotImplemented