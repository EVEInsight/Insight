import asyncio
from functools import partial


class Helpers(object):
    @staticmethod
    def get_nested_value(d: dict, default_value=None, *args):
        for k in args:
            try:
                if d is None:
                    raise AttributeError
                else:
                    tmp_next_val = d.get(k)
                    if tmp_next_val is None and not isinstance(k, str):
                        tmp_next_val = d.get(str(k))
                    d = tmp_next_val
            except AttributeError:
                return default_value
        return d if d is not None else default_value

    @classmethod
    async def async_get_nested_value(cls, d: dict, default_value=None, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(cls.get_nested_value, d, default_value, *args))
