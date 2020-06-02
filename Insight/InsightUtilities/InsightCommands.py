import asyncio
import difflib
import InsightExc
from .InsightSingleton import InsightSingleton
import datetime
import InsightLogger
from functools import partial


class InsightCommands(metaclass=InsightSingleton):
    def __init__(self):
        self.logger = InsightLogger.InsightLogger.get_logger('CommandParser', 'CommandParser.log')
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
            'lscan':    ['dscan', 'localscan', 'shipscan', 'scan', "lscan", "l", "s"],
            'lock':     ['lock'],
            'unlock':   ['unlock'],
            'quit':     ['quit'],
            'admin':    ['admin'],
            'prefix':   ['prefix'],
            'limits':   ['limits', "limit", "ratelimits", "rates"],
            'roll':     ["roll", "dice", "random"],
            'top':      ["top", "killstop", "topkills"]
        }
        self.all_commands = [c for i in self.commands.values() for c in i]
        self.notfound_timers = {}
        self.loop = asyncio.get_event_loop()
        self.lock = asyncio.Lock(loop=self.loop)

    def __similar(self, message_txt):
        return difflib.get_close_matches(message_txt.lower(), self.all_commands)

    def get_matching_coro(self, channel_id: int, prefixes: list, message_txt: str, **kwargs):
        msg_lower = self.strip_prefix(prefixes, message_txt).lower()
        for key, val in self.commands.items():
            if any(msg_lower.startswith(i) for i in val):
                coro = kwargs.get(key)
                if asyncio.iscoroutine(coro):
                    self.logger.info("{} command hit: {} available prefix count: {} coro command: {}".format(str(channel_id), True, len(prefixes), key))
                    return coro
                else:
                    raise InsightExc.Internal.InsightException("Could not call coroutine. Keyword argument missing.")
        self.logger.info("{} command hit: {} available prefix count: {} similar commands: {}".format(str(channel_id), False, len(prefixes), str(self.__similar(message_txt))))
        return None

    async def parse_and_run(self, channel_id: int, prefixes: list, message_txt: str, **kwargs):
        if not await self.is_command_async(prefixes, message_txt):
            return
        else:
            selected_coro = await self.loop.run_in_executor(None, partial(self.get_matching_coro,
                                                                                         channel_id, prefixes,
                                                                                         message_txt, **kwargs))
            if asyncio.iscoroutine(selected_coro):
                await selected_coro
                return
            else:
                await self.raise_notfound(channel_id, prefixes, message_txt)

    def is_command(self, prefixes: list, message_txt: str, channel_id: int = None) -> bool:
        command_hit = any(message_txt.startswith(i.lower()) for i in prefixes)
        if channel_id:
            self.logger.info("{} prefix hit: {} available prefix count: {}".format(str(channel_id),
                                                                                   command_hit, len(prefixes)))
        return command_hit

    async def is_command_async(self, prefixes: list, message_txt: str, channel_id: int = None) -> bool:
        return await self.loop.run_in_executor(None, partial(self.is_command, prefixes,
                                                                            message_txt, channel_id))

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
