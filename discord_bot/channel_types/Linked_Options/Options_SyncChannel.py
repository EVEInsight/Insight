from . import options_base
from .. import capRadar
import discord
from functools import partial
from sqlalchemy.orm import Session


class Options_Sync(options_base.Options_Base):
    def __init__(self, insight_channel):
        assert isinstance(insight_channel, capRadar.capRadar)
        super().__init__(insight_channel)

    async def InsightOption_addToken(self, message_object: discord.Message):
        """Add new token - Adds a new token for syncing contact information related to pilots, corporations, or alliances."""
        pass

    async def InsightOption_removeToken(self, message_object: discord.Message):
        """Remove token - Removes a token from the channel along with any synced contacts associated with it."""
        pass

    async def InsightOption_syncnow(self, message_object: discord.Message):
        """Force sync - Updates the channel's allies list if you have SSO tokens assigned to it."""
        pass


from discord_bot import discord_options as dOpt
from database.db_tables import *
