class MultiLock(object):
    def __init__(self, async_locks: list):
        self.locks = async_locks

    async def __aenter__(self):
        for a_lock in self.locks:
            await a_lock.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for a_lock in self.locks:
            try:
                a_lock.release()
            except RuntimeError: # lock is already released
                pass
