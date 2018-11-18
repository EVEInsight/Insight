class InsightMain(object):
    @classmethod
    def warning_filter(cls):
        import warnings
        from sqlalchemy.exc import SAWarning

        warnings.filterwarnings(action='ignore', category=SAWarning,
                                message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')
        warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')

    @classmethod
    def insight_run(cls, multiproc_dict):
        import InsightLogger
        InsightLogger.InsightLogger.logger_init()
        from service.service import service_module
        from discord_bot.discord_main import Discord_Insight_Client
        import sys
        import os

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
