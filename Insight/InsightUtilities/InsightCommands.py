import asyncio
import difflib
import InsightExc
from .InsightSingleton import InsightSingleton
import datetime


class InsightCommands(metaclass=InsightSingleton):
    def __init__(self, prefix_self: str = None):
        self.prefix_self = prefix_self
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
            'admin':    ['admin']
        }
        self.all_commands = [c for i in self.commands.values() for c in i]
        self.notfound_timers = {}

    def __similar(self, message_txt):
        return difflib.get_close_matches(message_txt.lower(), self.all_commands)

    def set_bot_mention_prefix(self, prefix: str):
        self.prefix_self = prefix

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
            self.raise_notfound(channel_id, prefixes, message_txt)

    def is_command(self, prefixes: list, message_txt: str)->bool:
        if self.prefix_self is not None and message_txt.startswith(self.prefix_self):
            return True
        else:
            return any(message_txt.startswith(i.lower()) for i in prefixes)

    def strip_prefix(self, prefixes: list, message_txt: str)->str:
        if self.prefix_self is not None:
            prefixes.append(self.prefix_self)
        for p in prefixes:
            if message_txt.startswith(p):
                new_str = message_txt.replace(p, "", 1)
                return new_str.strip()
        return message_txt

    def can_raise_notfound(self, channel_id: int)->bool:
        next_raise = self.notfound_timers.get(channel_id)
        if isinstance(next_raise, datetime.datetime):
            if datetime.datetime.utcnow() >= next_raise:
                self.notfound_timers[channel_id] = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
                return True
            else:
                return False
        else:
            self.notfound_timers[channel_id] = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
            return True

    def raise_notfound(self, channel_id: int, prefixes: list, message_txt: str):
        if self.can_raise_notfound(channel_id):
            prefix_s = str(self.prefix_self + " ") if len(prefixes) == 0 else min(prefixes, key=len)
            similar_commands = self.__similar(message_txt)
            resp_text = "The command: '{}' was not found.\n\n".format(message_txt)
            if len(similar_commands) == 0:
                resp_text += "No similar commands could be found matching what you entered.\n\n"
            else:
                resp_text += "Did you mean?\n\n"
                for c in similar_commands:
                    resp_text += "'{}{}'\n".format(prefix_s, c)
            resp_text += "\nRun the '{}help' command to see a list of available commands.".format(prefix_s)
            if len(resp_text) >= 750:
                raise InsightExc.userInput.CommandNotFound
            else:
                raise InsightExc.userInput.CommandNotFound(resp_text)
        else:
            return
