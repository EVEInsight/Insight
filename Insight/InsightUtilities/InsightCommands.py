import asyncio
import difflib
import InsightExc
from .InsightSingleton import InsightSingleton
import datetime


class InsightCommands(metaclass=InsightSingleton):
    def __init__(self):
        self.commands = {
            'about':    ['about', 'info'],
            'help':     ['help', 'commands'],
            'create':   ['create', 'new'],
            'settings': ['settings', 'modify', 'options', 'config'],
            'sync':     ['sync', 'ignorelists', 'list', 'blacklist'],
            'start':    ['start', 'resume'],
            'stop':     ['stop', 'pause'],
            'remove':   ['remove', 'delete'],
            'status':   ['status'],
            'eightball':['ball', '8ball', 'magic', '8'],
            'dscan':    ['dscan', 'localscan', 'shipscan', 'scan'],
            'lock':     ['lock'],
            'unlock':   ['unlock'],
            'quit':     ['quit'],
            'admin':    ['admin'],
            'prefix':   ['prefix']
        }
        self.all_commands = [c for i in self.commands.values() for c in i]
        self.notfound_timers = {}
        self.lock = asyncio.Lock(loop=asyncio.get_event_loop())

    def __similar(self, message_txt):
        return difflib.get_close_matches(message_txt.lower(), self.all_commands)

    async def parse_and_run(self, channel_id: int, prefixes: list, message_txt: str, **kwargs):
        if not self.is_command(prefixes, message_txt):
            return
        else:
            msg_lower = self.strip_prefix(prefixes, message_txt).lower()
            for key, val in self.commands.items():
                if any(msg_lower.startswith(i) for i in val):
                    coro = kwargs.get(key)
                    if asyncio.iscoroutine(coro):
                        await coro
                        return
                    else:
                        raise InsightExc.Internal.InsightException("Could not call coroutine. Keyword argument missing.")
            await self.raise_notfound(channel_id, prefixes, message_txt)

    def is_command(self, prefixes: list, message_txt: str)->bool:
        return any(message_txt.startswith(i.lower()) for i in prefixes)

    def strip_prefix(self, prefixes: list, message_txt: str)->str:
        for p in prefixes:
            if message_txt.startswith(p):
                new_str = message_txt.replace(p, "", 1)
                return new_str.strip()
        return message_txt

    def strip_non_command(self, prefixes, message_txt: str)->str:
        no_prefix = self.strip_prefix(prefixes, message_txt)
        if no_prefix == message_txt:  # not a command and has no prefix parsed out
            return message_txt
        for c in self.all_commands:
            if no_prefix.startswith(c):
                new_str = no_prefix.replace(c, "", 1)
                return new_str.strip()
        return no_prefix

    async def can_raise_notfound(self, channel_id: int)->bool:
        async with self.lock:
            next_raise = self.notfound_timers.get(channel_id)
            if isinstance(next_raise, datetime.datetime):
                if datetime.datetime.utcnow() >= next_raise:
                    self.notfound_timers[channel_id] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                    return True
                else:
                    return False
            else:
                self.notfound_timers[channel_id] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                return True

    async def raise_notfound(self, channel_id: int, prefixes: list, message_txt: str):
        if await self.can_raise_notfound(channel_id):
            prefix_s = "" if len(prefixes) == 0 else min(prefixes, key=len)
            similar_commands = self.__similar(message_txt)
            resp_text = "The command: '{}' was not found.\n\n".format(message_txt)
            if len(similar_commands) == 0:
                resp_text += "No similar commands could be found matching what you entered.\n\n"
            else:
                resp_text += "Did you mean?\n\n"
                for c in similar_commands:
                    resp_text += "'{}{}'\n".format(prefix_s, c)
            resp_text += "\nRun the '{0}help' command to see a list of available commands. You can manage Insight " \
                         "prefixes by running: '{0}prefix' to avoid command collisions with other Discord bots." \
                         "".format(prefix_s)
            if len(resp_text) >= 750:
                raise InsightExc.userInput.CommandNotFound
            else:
                raise InsightExc.userInput.CommandNotFound(resp_text)
        else:
            return
