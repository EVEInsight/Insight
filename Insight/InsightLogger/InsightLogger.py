import logging
import os
import datetime
import time
import sys


class InsightLogger(object):
    @classmethod
    def path(cls, file_name):
        tm = datetime.datetime.utcnow()
        tm_s = tm.strftime('%m_%d_%Y-')
        pt_name = 'logs/{}'.format(file_name.split('.', 1)[0])
        os.makedirs(pt_name, exist_ok=True)
        return os.path.join(pt_name, str(tm_s+file_name))

    @classmethod
    def get_logger(cls, name, file_name, level=logging.INFO, console_print=False)->logging.Logger:
        logger = logging.getLogger(name)
        if len(logger.handlers) == 0:
            logger.setLevel(level)
            if console_print:
                fmt = logging.Formatter('%(asctime)s - %(message)s')
                fmt.converter = time.gmtime
                sh_stdout = logging.StreamHandler(stream=sys.stdout)
                sh_stdout.setFormatter(fmt)
                sh_stdout.setLevel(level)
                logger.addHandler(sh_stdout)
            fh = logging.FileHandler(cls.path(file_name))
            fmt = logging.Formatter('%(asctime)s\t%(threadName)s:%(name)s\t%(levelname)s - %(message)s')
            fmt.converter = time.gmtime
            fh.setFormatter(fmt)
            fh.setLevel(level)
            logger.addHandler(fh)
        return logger

    @classmethod
    def logger_init(cls):
        cls.get_logger('urllib3', 'urllib3_requests.log', level=logging.DEBUG)
        cls.get_logger('discord', 'discord_asnycio.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.engine', 'sqlalchemy_engine.log', level=logging.WARNING)
        cls.get_logger('sqlalchemy.dialects', 'sqlalchemy_dialects.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.pool', 'sqlalchemy_pool.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.orm', 'sqlalchemy_orm.log', level=logging.WARNING)

