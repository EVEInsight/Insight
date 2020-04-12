import asyncio
import time


class ComparableFuture(object):
    def __init__(self, asyncio_future):
        self.future = asyncio_future
        self.time = time.time()

    def __lt__(self, other):
        return self.time < other.get_time()

    def __gt__(self, other):
        return self.time > other.get_time()

    def get_time(self):
        return self.time

    def get_future(self) -> asyncio.Future:
        return self.future
