import asyncio
import InsightExc
from functools import partial
from InsightUtilities.Misc.ComparableFuture import ComparableFuture


class LimitClient(object):
    def __init__(self, parent_limiter=None, provisioned_amount=1000, second_interval=1, id_name="", redact=False):
        if parent_limiter and not isinstance(parent_limiter, LimitClient):
            raise InsightExc.Internal.InsightException("Invalid parent limiter.")
        self.loop = asyncio.get_event_loop()
        self.parent_limiter: LimitClient = parent_limiter
        self.provisioned_amount = provisioned_amount
        self.semaphores = asyncio.BoundedSemaphore(value=self.provisioned_amount, loop=self.loop)
        self.interval = second_interval
        self.task_queue = asyncio.PriorityQueue(loop=self.loop)
        self.process_queue = self.loop.create_task(self._process_queue())
        self.identifier = id_name
        self.redact = redact
        self.pending_lock_max = 1000000000
        self.pending_lock_semaphores = asyncio.Semaphore(value=self.pending_lock_max, loop=self.loop)

    def limited(self) -> bool:
        return self.semaphores.locked()

    def remaining(self) -> int:
        return self.semaphores._value

    def get_pending_count(self) -> int:
        return self.pending_lock_max - self.pending_lock_semaphores._value

    def used_tickets(self):
        return self.provisioned_amount - self.remaining()

    def get_self_and_parent_stats(self, no_redact=False):
        stats = [self.stats(no_redact)]
        if self.parent_limiter:
            stats += self.parent_limiter.get_self_and_parent_stats(no_redact)
        return stats

    def usage_ratio(self):
        used_tickets = self.used_tickets()
        if used_tickets == 0:
            return 0
        else:
            return used_tickets / self.provisioned_amount

    def priority_value(self, high_priority=False) -> int:
        penalty = 100 if high_priority else 150
        return int((self.usage_ratio() * 100) + penalty)

    def stats(self, no_redact=False):
        if self.redact and not no_redact:
            return {"usage_ratio": round(self.usage_ratio() * 100, 1), "allocation": "REDACTED", "interval": "REDACTED",
                    "used_tickets": "REDACTED", "available": "REDACTED", "name": self.identifier,
                    "remaining_ratio": round((1 - self.usage_ratio()) * 100, 1), "queue_length": "REDACTED"}
        return {"usage_ratio": round(self.usage_ratio() * 100, 1), "allocation": self.provisioned_amount,
                "interval": self.interval, "used_tickets": self.used_tickets(), "available": self.remaining(),
                "name": self.identifier, "remaining_ratio": round((1 - self.usage_ratio()) * 100, 1),
                "queue_length": self.get_pending_count()}

    async def _process_queue(self):
        while True:
            try:
                r: tuple = await self.task_queue.get()
                cf: ComparableFuture = r[1]
                f = cf.get_future()
                await self._consume_ticket()
                self.loop.call_soon_threadsafe(partial(f.set_result, 0))
            except Exception as ex:
                print(ex)
                await asyncio.sleep(5)

    async def _consume_ticket_future_task(self, priority_level):
        async with self.pending_lock_semaphores:
            cf = ComparableFuture(asyncio.Future())
            f = cf.get_future()
            await self.task_queue.put((priority_level, cf))
            await f

    async def _consume_ticket(self):
        await self.semaphores.acquire()
        if self.parent_limiter:
            await self.parent_limiter._consume_ticket_future_task(self.priority_value())

    async def _release_ticket(self):
        if self.parent_limiter:
            await self.parent_limiter._release_ticket()
        self.loop.create_task(self._interval_release_task())

    async def _interval_release_task(self):
        await asyncio.sleep(self.interval)
        self.semaphores.release()

    async def __aenter__(self):
        await self._consume_ticket_future_task(priority_level=2)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._release_ticket()


class LimitClientHP(object):
    def __init__(self, limit_client_base):
        self.limit_client = limit_client_base

    def limited(self) -> bool:
        return self.limit_client.semaphores.locked()

    def remaining(self) -> int:
        return self.limit_client.semaphores._value

    async def __aenter__(self):
        await self.limit_client._consume_ticket_future_task(priority_level=1)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.limit_client._release_ticket()



