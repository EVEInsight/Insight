import discord
from database.db_tables import tb_servers, tb_server_prefixes
from sqlalchemy.orm import Session
from functools import partial
import InsightLogger
import asyncio


class ServerManager(object):
    def __init__(self, service_module, discord_client):
        self.service = service_module
        self.client: discord.Client = discord_client
        self.lock = asyncio.Lock(loop=self.client.loop)
        self.default_prefixes = ['?', '!']
        self.prefix_self = None
        self.guild_prefixes = {}
        self.lg = InsightLogger.InsightLogger.get_logger('Insight.command', 'Insight_command.log')

    def invalidate_prefixes(self, discord_guild: discord.Guild):
        if not isinstance(discord_guild, discord.Guild):
            return
        else:
            self.guild_prefixes[discord_guild.id] = None

    async def get_min_prefix(self, discord_channel: discord.TextChannel)->str:
        pref = await self.get_server_prefixes(discord_channel)
        return "" if len(pref) == 0 else min(pref, key=len)

    def get_append_self_prefix(self, prefix_list: list):
        if self.prefix_self is not None:
            return [self.prefix_self] + prefix_list
        else:
            return prefix_list

    async def get_server_prefixes(self, discord_channel: discord.TextChannel)->list:
        async with self.lock:
            if not isinstance(discord_channel, discord.TextChannel):
                return self.get_append_self_prefix(self.default_prefixes)
            else:
                guild: discord.Guild = discord_channel.guild
                items = self.guild_prefixes.get(guild.id)
            if isinstance(items, list):
                return items
            else:
                pulled_items = await self.client.loop.run_in_executor(None, partial(self.get_prefixes_from_db, guild))
                items = self.get_append_self_prefix(pulled_items)
                items.sort(key=len, reverse=True)
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

    def add_prefix(self, prefix: str, guild_obj: discord.Guild):
        db: Session = self.service.get_session()
        try:
            db.merge(tb_server_prefixes(guild_obj.id, prefix))
            db.commit()
            self.invalidate_prefixes(guild_obj)
        except Exception as ex:
            self.lg.exception(ex)
            raise ex
        finally:
            db.close()

    def remove_prefix(self, prefix: str, guild_obj: discord.Guild):
        db: Session = self.service.get_session()
        try:
            row = db.query(tb_server_prefixes).filter(tb_server_prefixes.server_id==guild_obj.id, tb_server_prefixes.prefix==prefix).one_or_none()
            if row is not None:
                db.delete(row)
            db.commit()
            self.invalidate_prefixes(guild_obj)
        except Exception as ex:
            self.lg.exception(ex)
            raise ex
        finally:
            db.close()

    async def populate_guilds(self):
        for channel in self.client.get_all_channels():
            await self.get_server_prefixes(channel)

    async def loader(self):
        self.prefix_self = self.client.user.mention
        await self.populate_guilds()
