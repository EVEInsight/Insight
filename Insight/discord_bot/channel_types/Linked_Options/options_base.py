import discord
from .. import base_object
import InsightExc
from sqlalchemy.orm import Session
from functools import partial
import traceback
from database.db_tables import tb_channels


class Options_Base(object):
    def __init__(self,insight_channel):
        assert isinstance(insight_channel,base_object.discord_feed_service)
        self.cfeed = insight_channel

    async def get_option_coroutines(self,required_only=False):
        for opt in self.yield_options():
            if required_only:
                if opt[1]:
                    yield opt[0]
            else:
                yield opt[0]

    def yield_options(self):
        return
        yield

    async def reload(self, message_object):
        await self.cfeed.async_load_table()
        if message_object is not None:
            await message_object.channel.send('ok')

    def __row_modify(self, row, merge=False):
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

    def __get_cached_row(self):
        db: Session = self.cfeed.service.get_session()
        try:
            return db.query(tb_channels).filter(tb_channels.channel_id == self.cfeed.channel_id).one()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def get_cached_copy(self)->tb_channels:
        row = await self.cfeed.discord_client.loop.run_in_executor(None, self.__get_cached_row)
        return row

    async def delete_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.__row_modify, row, False))

    async def save_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.__row_modify, row, True))

