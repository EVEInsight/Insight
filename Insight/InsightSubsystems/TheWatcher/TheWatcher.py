from InsightUtilities import InsightSingleton
import InsightLogger
from service import service
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import janus
from database.db_tables import tb_kills, tb_characters, tb_systems, tb_victims, tb_attackers
from InsightSubsystems.TheWatcher.WatcherTimers import WatcherTimers
from InsightSubsystems.TheWatcher.WatcherObjects import Pilot, SolarSystem
import traceback
import datetime


class TheWatcher(metaclass=InsightSingleton):
    def __init__(self, service_module):
        self.service: service.service_module = service_module
        self.systems_id = {}
        self.systems_name = {}
        self.constellations = {}
        self.regions = {}
        self.pilots_id = {}
        self.pilots_name = {}
        self.processed_mails = set()
        self.top_km_id = -1
        self.top_insert_time = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        self.loop = asyncio.get_event_loop()
        self.kmQueue = janus.Queue(maxsize=50000, loop=self.loop)
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=2)
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.main", "Watcher_main.log", console_print=True)
        InsightLogger.InsightLogger.get_logger("Watcher.Systems", "Watcher_Systems.log")
        InsightLogger.InsightLogger.get_logger("Watcher.Pilots", "Watcher_Pilots.log")
        self.lock_write = asyncio.Lock(loop=self.loop)
        self.timers = WatcherTimers.WatcherTimers(self)

    async def executor(self, functionPointer, *args):
        return await self.loop.run_in_executor(self.thread_pool, partial(functionPointer, *args))

    async def reset_all(self):
        async with self.lock_write:
            self.logger.info("Clearing all cached data and emptying the mail queue.")
            while True:
                try:
                    await self.kmQueue.async_q.get_nowait()
                except asyncio.QueueEmpty:
                    break
            self.systems_id = {}
            self.systems_name = {}
            self.constellations = {}
            self.regions = {}
            self.pilots_id = {}
            self.pilots_name = {}
            self.processed_mails = set()
            self.logger.info("Finished clearing all cached data and mail queue.")

    async def submit_km_noblock(self, km):
        self.loop.create_task(self.kmQueue.async_q.put(km))

    async def submit_km(self, km):
        await self.kmQueue.async_q.put(km)

    def submit_km_sync_block(self, km):
        self.kmQueue.sync_q.put(km)

    async def run_setup_tasks(self):
        self.loop.create_task(self.coroutine_dequeue())
        #self.loop.create_task(self.coroutine_enqueue())
        await self.timers.start_tasks()

    def get_pilot(self, pilot_multi):
        """id, name, or char sql object will get pilot. Returns the object else none if not loaded. Feeding sql object
        is the only method to load the char into the tables"""
        try:
            if isinstance(pilot_multi, str):
                return self.pilots_name.get(pilot_multi)  # lookup in name hash table
            elif isinstance(pilot_multi, int):
                return self.pilots_id.get(pilot_multi)
            elif isinstance(pilot_multi, tb_characters):
                pilot_obj = self.pilots_id.get(pilot_multi.get_id())
                if pilot_obj is None:
                    return Pilot.Pilot(pilot_multi, self)
                else:
                    return pilot_obj
            else:
                return None
        except Exception as ex:
            self.logger.exception("get_pilot")

    def get_system(self, system_multi):
        try:
            if isinstance(system_multi, tb_systems):
                system_obj = self.systems_id.get(system_multi.get_id())
                if system_obj is None:
                    return SolarSystem.SolarSystem(system_multi, self)
                else:
                    return system_obj
            else:
                return None
        except Exception as ex:
            self.logger.exception("get_system")

    def process_km(self, km):
        if not isinstance(km, tb_kills):
            self.logger.error("{} is not a killmail.".format(str(type(km))))
        for a in km.object_attackers:
            if isinstance(a, tb_attackers):
                sql_pilot = a.object_pilot
                if isinstance(sql_pilot, tb_characters):
                    watcher_pilot = self.get_pilot(sql_pilot)
                    if isinstance(watcher_pilot, Pilot.Pilot):
                        watcher_pilot.update_self(km, a)
        sql_victim = km.object_victim
        if isinstance(sql_victim, tb_victims):
            sql_pilot = sql_victim.object_pilot
            if isinstance(sql_pilot, tb_characters):
                watcher_pilot = self.get_pilot(sql_pilot)
                if isinstance(watcher_pilot, Pilot.Pilot):
                    watcher_pilot.update_self(km, sql_victim)
        self.processed_mails.add(km.kill_id)
        if km.kill_id > self.top_km_id:
            self.top_km_id = km.kill_id
        if km.loaded_time > self.top_insert_time:
            self.top_insert_time = km.loaded_time

    async def coroutine_dequeue(self):
        self.logger.info('The Watcher (pilot ship and system tracker) dequeue coroutine started.')
        while True:
            try:
                km: tb_kills = await self.kmQueue.async_q.get()
                async with self.lock_write:
                    km_id = km.kill_id
                    if km_id not in self.processed_mails:
                        await self.executor(self.process_km, km)
                        self.processed_mails.add(km_id)
            except Exception as ex:
                self.logger.exception("Enqueue mail")
