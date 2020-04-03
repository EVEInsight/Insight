import threading
import sys
import traceback


class InsightSingleton(type):
    __lock = threading.Lock()
    __init_locks = {}
    __instances = {}

    def __call__(cls, *args, **kwargs):
        with cls.__lock:
            lock = cls.__init_locks.get(cls.__name__)
            if lock is None:
                lock = threading.Lock()
                cls.__init_locks[cls.__name__] = lock
        with lock:
            if not cls.__instances.get(cls.__name__):
                try:
                    cls.__instances[cls.__name__] = super(InsightSingleton, cls).__call__(*args, **kwargs)
                except TypeError as ex:
                    print(ex)
                    traceback.print_stack()
                    sys.stderr.write("Singleton returned a non-init instance.\n")
                    sys.exit(1)
            return cls.__instances[cls.__name__]

    @classmethod
    def clear_instance_references(cls):
        with cls.__lock:
            cls.__init_locks = {}
            cls.__instances = {}

