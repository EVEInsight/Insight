import logging
import os
import datetime
import time
import sys
from logging.handlers import TimedRotatingFileHandler


class LoggerStartTime(object):
    def __init__(self):
        self.start = datetime.datetime.utcnow()

    def ms_passed(self)->int:
        return int((datetime.datetime.utcnow() - self.start).total_seconds() * 1000)

    def seconds_passed(self)->int:
        return int((datetime.datetime.utcnow() - self.start).total_seconds())


class InsightLogger(object):
    @classmethod
    def path(cls, file_name):
        fname = file_name.split('.', 1)[0]
        pt_name = 'logs/{}'.format(fname)
        os.makedirs(pt_name, exist_ok=True)
        return os.path.join(pt_name, fname)

    @classmethod
    def get_logger(cls, name, file_name, level=logging.INFO, console_print=False, console_level=logging.WARNING, child=False)->logging.Logger:
        logger = logging.getLogger(name)
        if len(logger.handlers) == 0 and not child:
            logger.setLevel(level)
            f_fmt = logging.Formatter('%(asctime)s %(threadName)23s:%(name)-40s %(levelname)-8s - %(message)s')
            f_fmt.converter = time.gmtime
            if console_print:
                if console_level >= logging.WARNING:
                    sh_console = logging.StreamHandler(stream=sys.stderr)
                    sh_console.setFormatter(f_fmt)
                else:
                    sh_console = logging.StreamHandler(stream=sys.stdout)
                    fmt = logging.Formatter('%(asctime)s - %(message)s')
                    fmt.converter = time.gmtime
                    sh_console.setFormatter(fmt)
                sh_console.setLevel(console_level)
                logger.addHandler(sh_console)
            fh = TimedRotatingFileHandler(cls.path(file_name), when='midnight', interval=1, backupCount=30, delay=True,
                                          utc=True, encoding="utf-8")
            fh.setFormatter(f_fmt)
            fh.setLevel(level)
            logger.addHandler(fh)
        return logger

    @classmethod
    def time_log(cls, logger_object: logging.Logger, start_time: LoggerStartTime, msg: str, warn_higher: int = 5000, seconds=False):
        if seconds:
            passed_time = start_time.seconds_passed()
            log_m = "Time: {:>4}s - {}".format(passed_time, msg)
        else:
            passed_time = start_time.ms_passed()
            log_m = "Time: {:>4}ms - {}".format(passed_time, msg)
        if passed_time >= warn_higher:
            logger_object.warning(log_m)
        else:
            logger_object.info(log_m)

    @classmethod
    def time_log_min(cls, logger_object: logging.Logger, start_time: LoggerStartTime, msg: str, min_ms: int = 5000):
        if start_time.ms_passed() >= min_ms:
            cls.time_log(logger_object, start_time, msg, min_ms, seconds=False)

    @classmethod
    def time_start(cls)->LoggerStartTime:
        return LoggerStartTime()

    @classmethod
    def logger_init(cls):
        cls.get_logger('urllib3', 'urllib3_requests.log', level=logging.DEBUG)
        cls.get_logger('discord', 'discord_asnycio.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.engine', 'sqlalchemy_engine.log', level=logging.WARNING)
        cls.get_logger('sqlalchemy.dialects', 'sqlalchemy_dialects.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.pool', 'sqlalchemy_pool.log', level=logging.INFO)
        cls.get_logger('sqlalchemy.orm', 'sqlalchemy_orm.log', level=logging.WARNING)
        cls.get_logger('Insight.feed', 'Insight_feed.log')
        cls.get_logger('Insight.filter', 'Insight_filter.log')
        cls.get_logger('Insight.command', 'Insight_command.log')
        cls.get_logger('Tokens', 'Tokens.log')
        cls.get_logger('InsightUtilities', 'InsightUtilities.log', level=logging.DEBUG)
        cls.get_logger('Subsystem', 'Subsystem.log', level=logging.DEBUG)
        cls.get_logger('Cache', 'Cache.log', level=logging.DEBUG)
        cls.get_logger('MailError', 'MailError.log', console_print=True, console_level=logging.WARNING)
