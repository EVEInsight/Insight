import threading
import sys
import traceback
import InsightLogger


class InsightSingleton(type):
    __lock = threading.Lock()
    __init_locks = {}
    __instances = {}
    logger = InsightLogger.InsightLogger.get_logger('InsightUtilities.InsightSingleton', 'InsightUtilities.log',
                                                    child=True)

    def __call__(cls, *args, **kwargs):
        cls_name = cls.__name__
        cls.logger.info("Request for {}".format(cls_name))
        with cls.__lock:
            lock = cls.__init_locks.get(cls_name)
            if lock is None:
                lock = threading.Lock()
                cls.__init_locks[cls_name] = lock
        with lock:
            if not cls.__instances.get(cls_name):
                cls.logger.info("Class '{}' does not exist yet. Attempting to create.".format(cls_name))
                try:
                    cls.__instances[cls_name] = super(InsightSingleton, cls).__call__(*args, **kwargs)
                except TypeError as ex:
                    print(ex)
                    traceback.print_stack()
                    sys.stderr.write("Singleton returned a non-init instance.\n")
                    cls.logger.exception(ex)
                    sys.exit(1)
            else:
                cls.logger.info("Class '{}' already exists. Returning existing instance at {}".
                                format(cls_name, id(cls.__instances[cls_name])))
            return cls.__instances[cls_name]

    @classmethod
    def clear_instance_references(cls):
        with cls.__lock:
            cls.__init_locks = {}
            cls.__instances = {}

