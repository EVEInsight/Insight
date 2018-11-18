class InsightMain(object):
    @classmethod
    def insight_run(cls, multiproc_dict):
        import InsightLogger
        InsightLogger.InsightLogger.logger_init()
        import warnings
        from sqlalchemy.exc import SAWarning
        from service.service import service_module
        from discord_bot.discord_main import Discord_Insight_Client
        import sys
        import os

        lg = InsightLogger.InsightLogger.get_logger('main', 'main.log')
        lg.info('Insight is starting.')

        warnings.filterwarnings(action='ignore', category=SAWarning,
                                message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')  # SDE price conversion error which can be ignored
        warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')  # async option coroutines that are created but never used

        service_mod = service_module()
        lg.info('Insight has completed service loading and setup.')
        Discord_Insight_Client.start_bot(service_mod, multiproc_dict)
        lg.info('Insight is shutting down with a clean exit.')
        sys.exit(0)
        lg.error('The application did not close properly. Using a hard exit with os._exit(0).')
        os._exit(0)
