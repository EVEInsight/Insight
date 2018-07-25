import discord
from .. import base_object
import InsightExc
from sqlalchemy.orm import Session
from functools import partial


class Options_Base(object):
    def __init__(self,insight_channel):
        assert isinstance(insight_channel,base_object.discord_feed_service)
        self.cfeed = insight_channel

    async def get_option_coroutines(self,required_only=False):
        for i in dir(self):
            if required_only and i.startswith("InsightOptionRequired_"):
                yield getattr(self,i)
            elif not required_only and (i.startswith("InsightOption_") or i.startswith("InsightOptionRequired_")):
                yield getattr(self,i)
            else:
                continue

    async def reload(self, message_object):
        await self.cfeed.async_load_table()
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
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    async def delete_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.__row_modify, row, False))

    async def save_row(self, row):
        await self.cfeed.discord_client.loop.run_in_executor(None, partial(self.__row_modify, row, True))
