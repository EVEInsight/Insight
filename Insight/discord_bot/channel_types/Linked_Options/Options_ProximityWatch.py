from . import Base_Feed
import discord
from functools import partial
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError
import InsightExc
from . import opt_capradar


class Options_ProximityIntel(opt_capradar):
    def yield_options(self):
        yield (self.InsightOptionRequired_addRegSys, True)
        yield (self.InsightOption_rmRegSys, False)
        yield (self.InsightOptionRequired_maxage, True)
        yield (self.InsightOption_sync, False)
        yield from super(opt_capradar, self).yield_options()

    async def InsightOptionRequired_addRegSys(self, message_object: discord.Message):
        """Add a new base system/region - Null"""
        await self.reload(message_object)

    async def InsightOption_rmRegSys(self, message_object: discord.Message):
        """Remove a base system/region - Null"""
        await self.reload(message_object)


