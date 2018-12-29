import threading


class InsightSingleton(type):
    __init_locks = {}
    __instances = {}

    def __call__(cls, *args, **kwargs):
        lock = cls.__init_locks.get(cls.__name__)
        if lock is None:
            lock = threading.Lock()
            cls.__init_locks[cls.__name__] = lock
        with lock:
            if not cls.__instances.get(cls.__name__):
                cls.__instances[cls.__name__] = super(InsightSingleton, cls).__call__(*args, **kwargs)
            return cls.__instances[cls.__name__]
