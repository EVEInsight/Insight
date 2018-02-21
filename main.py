import argparse
import configparser

from bot.discord_bot import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c",
                        help="specifies a config file other than the default config.ini to run the program with",
                        default="config.ini")
    parser.add_argument("--skip_gen", "-sg",
                        help="skips re-downloading of api data and database import/updates of api",
                        action='store_true',
                        default=False)
    parser.add_argument("--disable_zKill", "-d_zk",
                        help="Disables the zKill API pulling thread operation",
                        action='store_true',
                        default=False)
    parser.add_argument("--disable_EntityUpdates", "-d_EU",
                        help="Disables the EntityUpdates API pulling thread operation",
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    config_file = configparser.ConfigParser()
    config_file.read(args.config)

    D_client.bot_run(config_file, args)

if __name__ == '__main__':
        main()