import InsightLogger
InsightLogger.InsightLogger.logger_init()
import warnings
from sqlalchemy.exc import SAWarning
from service.service import service_module
from discord_bot.discord_main import Discord_Insight_Client
import os


class Main(object):
    @classmethod
    def main(cls):
        lg = InsightLogger.InsightLogger.get_logger('main', 'main.log')
        lg.info('Insight is starting.')

        warnings.filterwarnings(action='ignore', category=SAWarning,
                                message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')  # SDE price conversion error which can be ignored
        warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')  # async option coroutines that are created but never used

        service_mod = service_module()
        lg.info('Insight has completed service loading and setup.')
        Discord_Insight_Client.start_bot(service_mod)
        os._exit(0)


if __name__ == "__main__":
    Main.main()
