from service.service import service_module
from discord_bot.discord_main import Discord_Insight_Client
import warnings
from sqlalchemy.exc import SAWarning
import sys
import os


def warning_filter():
    warnings.filterwarnings(action='ignore', category=SAWarning,
                            message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')
    warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')


def main():
    warning_filter()
    service_mod = service_module()
    Discord_Insight_Client.start_bot(service_mod)
    sys.exit(0)
    print('The application did not close properly. Using a hard exit with os._exit(0).')
    os._exit(0)


if __name__ == "__main__":
    main()