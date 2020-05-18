import asyncio
from functools import partial


class Helpers(object):
    @staticmethod
    def get_nested_value(d: dict, default_value=None, *args):
        for k in args:
            try:
                d = d.get(str(k))
            except AttributeError:
                return default_value
        return d if d is not None else default_value

    @classmethod
    async def async_get_nested_value(cls, d: dict, default_value=None, tp=None, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(tp, partial(cls.get_nested_value, d, default_value, *args))
