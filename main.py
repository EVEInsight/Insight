from service.service import service_module
from discord_bot.discord_main import Discord_Insight_Client


def main():
    service_mod = service_module()
    Discord_Insight_Client.start_bot(service_mod)

if __name__ == "__main__":
    main()