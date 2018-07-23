from service.service import service_module
from discord_bot.discord_main import Discord_Insight_Client
import warnings
from sqlalchemy.exc import SAWarning


def warning_filter():
    warnings.filterwarnings(action='ignore', category=SAWarning,
                            message='Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively,[\s\S]+')
    warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='[\s\S]+ was never awaited')


def main():
    warning_filter()
    service_mod = service_module()
    Discord_Insight_Client.start_bot(service_mod)


if __name__ == "__main__":
    main()