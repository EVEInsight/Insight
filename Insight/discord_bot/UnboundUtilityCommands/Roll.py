from .UnboundCommandBase import *
import discord
import random
from functools import partial
import InsightExc


class Roll(UnboundCommandBase):
    def do_roll_int(self, lower_bound: int, upper_bound: int) -> int:
        return random.randint(lower_bound, upper_bound)

    def make_int(self, val):
        return int(val)

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) -> str:
        #args = await self.unbound.split_text(message_text)
        lower_bound = 0
        upper_bound = 100
        # if len(args) == 1: #todo args
        #     try:
        #         upper_bound = int(args[0])
        #     except ValueError:
        #         raise InsightExc.userInput.InvalidInput("Invalid number. Usage '!roll upper_bound'.\nEx: '!roll 1000'")
        roll = await self.loop.run_in_executor(None, partial(self.do_roll_int, lower_bound, upper_bound))
        return "**{}** rolled a **{}**\n\n**Possible values**\nLower bound: {}\nUpper bound: {}"\
            .format(d_message.author.name, roll, lower_bound, upper_bound)

