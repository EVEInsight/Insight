import threading
import sys


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
                    cls.__instances[cls.__name__] = super(InsightSingleton, cls).__call__(*args, **kwargs)
                return cls.__instances[cls.__name__]

    def get_instantiated(cls):
        """Returns the instance without providing arguments.
        This instance must be instantiated first before calling this method."""
        with cls.__lock:
            inst = cls.__instances.get(cls.__name__)
            if inst is None:
                sys.stderr.write("Attempting to obtain class of type: '{}' before it was instantiated. "
                                 "Please file a bug report for this programming error.\n".format(cls.__name__))
                sys.exit(1)
            else:
                return inst

    @classmethod
    def clear_instance_references(cls):
        with cls.__lock:
            cls.__init_locks = {}
            cls.__instances = {}
