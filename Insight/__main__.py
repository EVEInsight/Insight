import InsightLogger
InsightLogger.InsightLogger.logger_init()
from service.service import service_module
from discord_bot.discord_main import Discord_Insight_Client
import warnings
from sqlalchemy.exc import SAWarning
import sys
import os
import multiprocessing


class Main(object):

    @classmethod
    def warning_filter(cls):
        warnings.filterwarnings(action='ignore', category=SAWarning,
                                message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')
        warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')

    @classmethod
    def insight_run(cls, multiproc_dict):
        lg = InsightLogger.InsightLogger.get_logger('main', 'main.log')
        lg.info('Insight is starting.')
        cls.warning_filter()
        service_mod = service_module()
        lg.info('Insight has completed service loading and setup.')
        Discord_Insight_Client.start_bot(service_mod, multiproc_dict)
        lg.info('Insight is shutting down with a clean exit.')
        sys.exit(0)
        lg.error('The application did not close properly. Using a hard exit with os._exit(0).')
        os._exit(0)

    @classmethod
    def main(cls):
        manager = multiprocessing.Manager()
        shared_dict = manager.dict()
        shared_dict['flag_reboot'] = True
        while shared_dict.get('flag_reboot') is True:
            shared_dict['flag_reboot'] = False
            p1 = multiprocessing.Process(target=cls.insight_run, args=(shared_dict,))
            p1.start()
            try:
                p1.join()
            except KeyboardInterrupt:
                if p1.is_alive():
                    print('Child process is still alive. Parent waiting to force terminate process.')
                    p1.terminate()
                    p1.join()
                sys.exit(0)
            if p1.exitcode != 0:
                shared_dict['flag_reboot'] = False
                sys.exit(p1.exitcode)
            else:
                if shared_dict['flag_reboot'] is True:
                    print('Insight is rebooting.')
                else:
                    break


if __name__ == "__main__":
    multiprocessing.freeze_support()
    Main.main()
