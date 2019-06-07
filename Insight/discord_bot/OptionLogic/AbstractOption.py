from discord_bot.channel_types import base_object
from discord_bot import discord_options as dOpt
from functools import partial
from sqlalchemy.orm import Session
from typing import List
import InsightExc
import discord
import traceback
from database.db_tables import tb_channels
from InsightUtilities import TextLoader


class AbstractOption(object):
    def __init__(self, cfeed, dMessage=None):
        self.cfeed: base_object.discord_feed_service = cfeed
        self.cID = self.cfeed.channel_id
        self.service = self.cfeed.service
        self.message: discord.Message = dMessage

    def _get_row(self) -> tb_channels:  # careful when using in direct messages
        """returns a cached copy of the row"""
        return self.cfeed.cached_feed_table

    async def _run_command(self):
        raise NotImplementedError

    def get_description(self) -> str:
        raise NotImplementedError

    async def run_message(self, message_object: discord.Message):
        """Option -> Replace this option text to be picked up by option loader wheel. New format."""
        self.message = message_object
        await self.run()

    async def run(self):
        await self._run_command()
        await self._reload(self.message)

    async def _executor(self, functionPointer, *args):
        return await self.cfeed.discord_client.loop.run_in_executor(None, partial(functionPointer, *args))

    async def _reload(self, message_object):  # todo remove copies from options main
        await self.cfeed.async_load_table()
        if message_object is not None:
            await message_object.channel.send('ok')

    def _row_modify(self, row, merge=False):
        db: Session = self.cfeed.service.get_session()
        try:
            if merge:
                db.merge(row)
            else:
                db.delete(row)
            db.commit()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    def _get_cached_row(self):
        db: Session = self.cfeed.service.get_session()
        try:
            return db.query(tb_channels).filter(tb_channels.channel_id == self.cfeed.channel_id).one()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def get_cached_copy(self) -> tb_channels:
        row = await self.cfeed.discord_client.loop.run_in_executor(None, self._get_cached_row)
        return row

    async def _delete_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self._row_modify, row, False))

    async def _save_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self._row_modify, row, True))
