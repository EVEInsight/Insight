import queue
import discord_bot as insightClient
import asyncio
import random
import discord
from functools import partial
import service as Service
import database.db_tables as dbRow
from sqlalchemy.orm import Session
from .FiltersVisualsEmbedded import *
import InsightExc
from sqlalchemy.orm.exc import NoResultFound
import datetime
import janus
import traceback
import errno


class discord_feed_service(object):
    def __init__(self,channel_discord_object:discord.TextChannel, service_object):
        assert isinstance(service_object,Service.ServiceModule)
        self.channel_discord_object = channel_discord_object
        self.channel_id = channel_discord_object.id
        self.service = service_object
        self.channel_manager = self.service.channel_manager
        self.discord_client = self.service.channel_manager.get_discord_client()

        self.kmQueue = janus.Queue(loop=self.discord_client.loop)
        self.__deque_task = None
        self.linked_options = self.get_linked_options()
        self.setup_table()
        self.template_loader()
        self.load_table()
        self.last_mention = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        self.appearance_class = None
        self.lock = asyncio.Lock(loop=self.discord_client.loop)

    def can_mention(self):
        return (self.last_mention + datetime.timedelta(minutes=self.mention_next())) <= datetime.datetime.utcnow()

    def mentioned(self):
        self.last_mention = datetime.datetime.utcnow()

    def mention_next(self)->int:
        try:
            return abs(self.cached_feed_table.mention_every)
        except Exception as ex:
            print(ex)
            return 15

    def set_deque_task(self,deq_task:asyncio.Task):
        assert isinstance(deq_task,asyncio.Task)
        self.__deque_task = deq_task

    def deque_done(self):
        try:
            assert isinstance(self.__deque_task,asyncio.Task)
            return self.__deque_task.done()
        except AssertionError:
            return True

    def setup_table(self):
        """make the related table if it does not yet exist"""
        if self.linked_table().make_row(self.get_object_id(), self.service, self.get_template_id()):
            pass
        else:
            raise InsightExc.Db.DatabaseError

    def get_object_id(self):
        return self.channel_id

    def load_table(self):
        self.cached_feed_table:dbRow.tb_channels = self.general_table().get_row(self.channel_id, self.service)
        # must be set to sqlalchemy channel specific object ex self.cached_feed_specific.object_enfeed

    def template_loader(self):
        pass

    async def async_load_table(self):
        await self.discord_client.loop.run_in_executor(None, self.load_table)

    def check_permission(self, user_author: discord.User, required_level, ignore_channel_setting=False):
        """
        :param user_author: discord user author or channel member
        :param required_level: level checked against. 0-no permission needed, 1-channel manage, 2-console/server admin
        :param ignore_channel_setting: Check permission even if channel is unlocked
        :return: void() else raise InsightExc.DiscordError.LackPermission on unauthorized access
        """
        if required_level == 0:
            return
        if not ignore_channel_setting and not self.is_loadable_feed():
            return
        if not ignore_channel_setting and not self.cached_feed_table.modification_lock:
            return
        p: discord.Permissions = user_author.permissions_in(self.channel_discord_object)
        if required_level == 1:
            if p.administrator or p.manage_roles or p.manage_messages or p.manage_guild or p.manage_channels or p.manage_webhooks:
                return
            else:
                raise InsightExc.DiscordError.LackPermission
        elif required_level == 2:
            if not self.service.is_admin(user_author.id):
                raise InsightExc.DiscordError.LackPermission('You must be an Insight admin to use this command.')
        else:
            print('Unknown permission level {}'.format(required_level))
            raise InsightExc.DiscordError.LackPermission

    async def proxy_lock(self, awaitable_coro, user_author, required_level, ignore_channel_setting=False):
        """call a command coroutine by proxy with a lock to prevent multiple commands running at once i.e: !settings"""
        self.check_permission(user_author, required_level, ignore_channel_setting)
        time_limit = datetime.datetime.utcnow() + datetime.timedelta(seconds=15)
        while self.lock.locked():  # timeout after 15 seconds of waiting. async wait_for has issues in 3.6
            if datetime.datetime.utcnow() >= time_limit:
                raise InsightExc.DiscordError.LockTimeout
            await asyncio.sleep(1)
        async with self.lock:
            if not self.channel_manager.exists(self) and self.is_loadable_feed():
                raise InsightExc.DiscordError.UnboundFeed
            await awaitable_coro

    async def command_create(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_sync(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_about(self, message_object):
        """!about - Display Insight credits and version information."""
        msg = "Insight {} by Nathan-LS. An EVE Online killmail feed" \
              " bot for Discord.\n\nhttps://github.com/Nathan-LS/Insight".format(str(self.service.get_version()))
        await message_object.channel.send(msg)

    async def command_help(self,message_object):
        """!help - Display information about available commands."""

        def get_commands():
            for i in dir(self):
                if i.startswith("command_"):
                    yield getattr(self, i)
                else:
                    continue

        resp_str = "These are all of the available commands usable in this channel:\n\n"
        for i in get_commands():
            info = i.__doc__
            if info is not None:
                resp_str += "{}\n\n".format(info)
        resp_str += "\nFor more detailed command, feed type, or configuration information check out the project wiki:\nhttps://github.com/Nathan-LS/Insight/wiki"
        await message_object.channel.send("{}\n{}".format(message_object.author.mention, resp_str))

    async def command_settings(self,message_object):
        """!settings - Modify Insight settings related to this channel or user."""
        __options = insightClient.mapper_index_withAdditional(self.discord_client,message_object)
        __options.set_main_header("Select an option to modify:")
        async for cor in self.linked_options.get_option_coroutines():
            __options.add_option(insightClient.option_calls_coroutine(cor.__doc__,"",cor(message_object)))
        await __options()

    async def command_start(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_stop(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_remove(self,message_object:discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_status(self, message_object: discord.Message):
        await self.command_not_supported_sendmessage(message_object)

    async def command_lock(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    async def command_unlock(self, message_object):
        await self.command_not_supported_sendmessage(message_object)

    def add_km(self,km):
        if self.cached_feed_table.feed_running:
            assert isinstance(km,dbRow.tb_kills)
            __visual = self.linked_visual(km)
            if __visual:
                self.kmQueue.sync_q.put_nowait(__visual)

    def add_message(self,message_text):
        if self.cached_feed_table.feed_running:
            self.kmQueue.sync_q.put_nowait(message_text)

    def linked_visual(self,km_row):
        subc = self.linked_visual_subc()
        return subc(km_row, self.channel_discord_object, self.cached_feed_table, self.cached_feed_specific, self)

    def make_derived_visual(self, visual_class):
        return visual_class

    def linked_visual_subc(self):
        try:
            if self.appearance_class.appearance_id() != self.cached_feed_table.appearance_id:
                raise InsightExc.Internal.VisualAppearanceNotEquals
        except:
            self.appearance_class = self.make_derived_visual(
                self.linked_visual_base().get_appearance_class(self.cached_feed_table.appearance_id))
        finally:
            return self.appearance_class

    def linked_visual_base(self):
        raise NotImplementedError
        # return visual_enfeed

    async def post_all(self):
        while self.channel_manager.exists(self):
            try:
                __item = await asyncio.wait_for(self.kmQueue.async_q.get(), timeout=3600)
            except asyncio.TimeoutError:
                continue
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                continue
            try:
                async with self.lock:
                    if self.cached_feed_table.feed_running and self.channel_manager.exists(self):
                        if isinstance(__item, base_visual):
                            await __item()
                            await self.channel_manager.add_delay(__item.get_load_time())
                        else:
                            await self.channel_discord_object.send(str(__item))
            except discord.Forbidden:
                try:
                    await self.channel_discord_object.send(
                        "Permissions are incorrectly set for the bot. See https://github.com/Nathan-LS/Insight#permissions\n\nRun the '!start' command to resume the feed once permissions are correctly set.")
                except:
                    pass
                finally:
                    await self.remove()
            except discord.HTTPException as ex:
                try:
                    if ex.status == 404:  # channel deleted
                        await self.channel_manager.delete_feed(self.channel_id)
                    elif 500 <= ex.status < 600:
                        if isinstance(__item, base_visual):
                            await self.kmQueue.async_q.put(__item)
                    else:
                        print('Error {} - when sending KM. discord.HTTPException'.format(ex.status))
                except Exception as ex:
                    print(ex)
            except InsightExc.DiscordError.MessageMaxRetryExceed:
                print('Error - max message retry limit exceeded when sending KM.')
                continue
            except OSError as ex:
                if ex.errno == errno.ECONNRESET or ex.errno == errno.ENETRESET:
                    if isinstance(__item, base_visual):
                        await self.kmQueue.async_q.put(__item)
                else:
                    print('Error {} - when sending KM. OSError'.format(ex))
            except Exception as ex:
                print('Error {} - when sending KM. Other'.format(ex))
                traceback.print_exc()
            await asyncio.sleep(.1)

    async def remove(self):
        """Temp pause an error feed instead of removing it completely. Resume again in 45 minutes."""
        try:
            if self.cached_feed_table.feed_running:
                remaining = 90
                self.cached_feed_table.feed_running = False
                while remaining > 0 and not self.cached_feed_table.feed_running:
                    remaining -= 1
                    await asyncio.sleep(30)
                await self.async_load_table()
        except Exception as ex:
            print(ex)

    async def delete(self):
        def non_async_delete():
            db:Session = self.service.get_session()
            try:
                __row = db.query(dbRow.tb_channels).filter(dbRow.tb_channels.channel_id == self.channel_id).one()
                db.delete(__row)
                db.commit()
                print('Deleted {} in {}'.format(str(self), self.str_channel_server()))
                return True
            except Exception as ex:
                print(ex)
                db.rollback()
                return False
            finally:
                db.close()

        return await self.discord_client.loop.run_in_executor(None, non_async_delete)

    async def command_not_supported_sendmessage(self, message_object:discord.Message):
        await message_object.channel.send("{}\nThis command is not supported in channel of type: {}\n".format(message_object.author.mention,str(self)))

    async def background_contact_sync(self, message=None, suppress=False):
        pass

    @classmethod
    def str_more_help(cls):
        return "Run the command '!help' to see a list of available commands or visit:\n\nhttps://github.com/Nathan-LS/Insight/wiki"

    def __str__(self):
        return "Base Insight Object"

    def str_channel_server(self):
        return_str = "channel_name(server_name)"
        try:
            channel_name = str(self.channel_discord_object.name)
            server_name = str(self.channel_discord_object.guild.name)
            return_str = '{}({})'.format(channel_name, server_name)
        except:
            pass
        finally:
            return str(return_str)

    @classmethod
    def general_table(cls)->dbRow.tb_channels:
        return dbRow.tb_channels

    @classmethod
    def linked_table(cls)->dbRow.tb_discord_base:
        raise NotImplementedError

    def get_linked_options(self):
        return Linked_Options.opt_base(self)

    @classmethod
    async def load_new(cls,channel_object:discord.TextChannel,service_module, discord_client):
        assert isinstance(channel_object,discord.TextChannel)
        return await discord_client.loop.run_in_executor(None, partial(cls,channel_object,service_module))

    @classmethod
    def get_template_id(cls):
        return None  # no template id exists

    @classmethod
    def get_template_desc(cls):
        return ""

    @classmethod
    def is_preconfigured(cls):
        return False

    @staticmethod
    def send_km(km,feed_channel):
        try:
            assert isinstance(km,dbRow.tb_kills)
            feed_channel.add_km(km)
        except Exception as ex:
            print(ex)

    @classmethod
    def is_loadable_feed(cls):
        return False

from . import Linked_Options


