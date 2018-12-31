import discord
from database.db_tables import tb_servers, tb_server_prefixes
from sqlalchemy.orm import Session
from functools import partial
import InsightLogger


class ServerManager(object):
    def __init__(self, service_module, discord_client):
        self.service = service_module
        self.client: discord.Client = discord_client
        self.default_prefixes = ['?', '!']
        self.prefix_self = None
        self.guild_prefixes = {}
        self.lg = InsightLogger.InsightLogger.get_logger('Insight.command', 'Insight_command.log')

    def invalidate_prefixes(self, discord_channel: discord.TextChannel):
        if not isinstance(discord_channel, discord.TextChannel):
            return
        else:
            self.guild_prefixes[discord_channel.guild.id] = None

    async def get_server_prefixes(self, discord_channel: discord.TextChannel)->list:
        if not isinstance(discord_channel, discord.TextChannel):
            return self.default_prefixes
        else:
            guild: discord.Guild = discord_channel.guild
            items = self.guild_prefixes.get(guild.id)
        if isinstance(items, list):
            return items
        else:
            items = await self.client.loop.run_in_executor(None, partial(self.get_prefixes_from_db, guild))
            if self.prefix_self is not None:
                items.append(self.prefix_self)
            self.guild_prefixes[guild.id] = items
            self.lg.info("Loaded prefixes from DB for server ID: {}".format(guild.id))
            return items

    def get_prefixes_from_db(self, guild_obj: discord.Guild)->list:
        db: Session = self.service.get_session()
        try:
            row: tb_servers = db.query(tb_servers).filter(tb_servers.server_id == guild_obj.id).one_or_none()
            if row is not None:
                row.server_name = guild_obj.name
                db.merge(row)
                db.commit()
                return [p.prefix for p in row.object_prefixes]
            else:
                row = tb_servers.get_row(guild_obj.id, self.service)
                row.server_name = guild_obj.name
                db.merge(row)
                for p in self.default_prefixes:
                    db.merge(tb_server_prefixes(guild_obj.id, p, load_fk=False))
                db.commit()
                return self.default_prefixes
        except Exception as ex:
            self.lg.exception(ex)
            return self.default_prefixes
        finally:
            db.close()

    async def populate_guilds(self):
        for channel in self.client.get_all_channels():
            await self.get_server_prefixes(channel)

    async def loader(self):
        self.prefix_self = self.client.user.mention
        await self.populate_guilds()
