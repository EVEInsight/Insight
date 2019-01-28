from tests.abstract import DatabaseTesting, AsyncTesting
from service import zk
import asyncio
from database.db_tables.eve import tb_kills
from tests.mocks import ServiceModule
import time
import queue
import janus
import os
import sys
import unittest
import requests
import aiohttp


class TestZk(DatabaseTesting.DatabaseTesting, AsyncTesting.AsyncTesting):

    @classmethod
    def setUpClass(cls):
        AsyncTesting.AsyncTesting.setUpClass()
        DatabaseTesting.DatabaseTesting.setUpClass()
        cls.zk_redis_working = False
        cls.zk_ws_working = False

    @classmethod
    def set_zk_redis_working(cls):
        cls.zk_redis_working = True

    @classmethod
    def set_zk_ws_working(cls):
        cls.zk_ws_working = True

    @classmethod
    def get_zk_redis_working(cls):
        return cls.zk_redis_working

    @classmethod
    def get_zk_ws_working(cls):
        return cls.zk_ws_working

    def setUp(self):
        AsyncTesting.AsyncTesting.setUp(self)
        self.resources = None
        DatabaseTesting.DatabaseTesting.setUp(self)
        sys.argv.extend(['-km', "74647898", "-fc", "-limit", "1"])
        self.service = ServiceModule.ServiceModule(self.scoped_session)
        self.set_resource_path("db_tables", "eve", "mails")
        self.zk = zk.zk(self.service)
        self.loop.run_until_complete(self.zk.make_queues())
        self.zk.run_websocket = True
        self.start_event_loop()
        self.data = self.file_json("74647898.json").get("package")

    def tearDown(self):
        DatabaseTesting.DatabaseTesting.tearDown(self)
        AsyncTesting.AsyncTesting.tearDown(self)
        if os.path.exists("zk_identifier.txt"):
            os.remove("zk_identifier.txt")

    @unittest.SkipTest
    def test_add_delay(self):  # todo
        self.fail()

    @unittest.SkipTest
    def test_avg_delay(self):  # todo
        self.fail()

    @unittest.SkipTest
    def test_get_stats(self):  # todo
        self.fail()

    def test_generate_redisq_url(self):
        with self.subTest("no_identifier=True"):
            self.assertEqual("https://redisq.zkillboard.com/listen.php", self.zk.generate_redisq_url(True))
        with self.subTest("no_identifier=False"):
            self.assertTrue(self.zk.generate_redisq_url(False).startswith("https://redisq.zkillboard.com/listen.php?queueID="))

    def test_generate_identifier(self):
        self.tearDown()
        identifier = self.zk.generate_identifier()
        self.assertIsInstance(identifier, str)
        self.assertEqual(8, len(identifier))
        self.assertTrue(os.path.exists("zk_identifier.txt"))
        with open("zk_identifier.txt") as f:
            self.assertEqual(identifier, f.read())

    def test_01_url_stream(self):
        self.zk.zk_stream_url = self.zk.generate_redisq_url(no_identifier=True)
        response = requests.get(url=self.zk.url_stream(), headers=self.service.get_headers(lib_requests=True), timeout=15)
        self.assertEqual(response.status_code, 200)
        data = response.json().get("package")
        if data is None:
            print("No pending mails.")
        else:
            self.assertIsInstance(data.get("killID"), int)
            km = data.get("killmail")
            for a in km.get("attackers"):
                self.assertTrue("damage_done" in a)
                self.assertIsInstance(a.get("final_blow"), bool)
                self.assertTrue(any(k in a for k in ["ship_type_id", "alliance_id", "corporation_id", "character_id"]))
                # self.assertTrue("weapon_type_id" in a)
            self.assertIsInstance(km.get("killmail_id"), int)
            self.assertIsInstance(km.get("killmail_time"), str)
            self.assertIsInstance(km.get("solar_system_id"), int)
            v = km.get("victim")
            self.assertTrue(any(k in v for k in ["ship_type_id", "alliance_id", "corporation_id", "character_id"]))
            self.assertIsInstance(v.get("items"), list)
            self.assertIsInstance(v.get("position").get("x"), (int, float))
            self.assertIsInstance(v.get("position").get("y"), (int, float))
            self.assertIsInstance(v.get("position").get("z"), (int, float))
            zkb = data.get("zkb")
            self.assertIsInstance(zkb.get("locationID"), int)
            self.assertIsInstance(zkb.get("hash"), str)
            self.assertIsInstance(zkb.get("fittedValue"), (int, float))
            self.assertTrue(zkb.get("totalValue"), (int, float))
            self.assertIsInstance(zkb.get("points"), (int, float))
            self.assertIsInstance(zkb.get("npc"), bool)
            self.assertIsInstance(zkb.get("solo"), bool)
            self.assertIsInstance(zkb.get("awox"), bool)
            self.assertIsInstance(zkb.get("href"), str)
        self.set_zk_redis_working()

    async def async_test_url_websocket(self):
        async with aiohttp.ClientSession(headers=self.service.get_headers()) as client:
            async with client.ws_connect(self.zk.url_websocket()) as ws:
                ws.send_json(data={"action": "sub", "channel": "killstream"})
                self.set_zk_ws_working()
                return

    def test_02_url_websocket(self):
        f = asyncio.run_coroutine_threadsafe(self.async_test_url_websocket(), self.loop)
        f.result()

    def test__make_km(self):
        with self.subTest("new"):
            mail = self.zk._make_km(self.data)
            self.assertIsInstance(mail, tb_kills)
            for a in mail.object_attackers + [mail.object_victim]:
                self.assertNotEqual(None, a.object_pilot.character_name)
                self.assertNotEqual(None, a.object_corp.corporation_name)
                if a.object_alliance is not None:
                    self.assertNotEqual(None, a.object_alliance.alliance_name)
                if a.object_ship is not None:
                    self.assertNotEqual(None, a.object_ship.type_name)
            self.assertNotEqual(None, mail.object_system.name)
        with self.subTest("existing"):
            self.assertEqual(None, self.zk._make_km(self.data))
        with self.subTest("error"):
            self.assertEqual(None, self.zk._make_km({}))

    def test_debug_simulate(self):
        asyncio.run_coroutine_threadsafe(self.zk.coroutine_filters(self.thread_Pool), self.loop)
        mail = tb_kills.make_row(self.data, self.service)
        self.zk._km_postProcess.sync_q.put_nowait(mail)
        self.zk.debug_simulate()
        time.sleep(.3)
        self.assertTrue(mail in self.service.channel_manager.mock_mails_sent)
        messages = self.service.channel_manager.mock_messages_sent
        self.assertTrue(
            'Starting debug mode.\nStarting KM ID: 74647898\nForce time to now: True\nKM Limit: 1\n' in messages)
        self.assertTrue('Debugging is now finished. Switching back to streaming live kms.' in messages)

    def test_03_pull_kms_redisq(self):
        self.zk.zk_stream_url = self.zk.generate_redisq_url(no_identifier=True)
        asyncio.run_coroutine_threadsafe(self.zk.pull_kms_redisq(), self.loop)
        try:
            item = self.zk._km_preProcess.sync_q.get(block=True, timeout=15)
        except queue.Empty:
            if not self.get_zk_redis_working():
                self.fail("Took too long to get a response from websocket. This does not necessarily mean the test failed,"
                          " there just might be little activity from endpoint at the moment.")
            print("No mails arrived in allotted time.")
            return
        self.assertIsInstance(item, dict)
        self.assertIsInstance(tb_kills.make_row(item, self.service), tb_kills)

    # def test_ws_extract(self): #implied pass if pull_kms_ws passes
    #     self.fail()

    def test_04_pull_kms_ws(self):
        asyncio.run_coroutine_threadsafe(self.zk.pull_kms_ws(), self.loop)
        try:
            item = self.zk._km_preProcess.sync_q.get(block=True, timeout=15)
        except queue.Empty:
            if not self.get_zk_ws_working():
                self.fail("Took too long to get a response from websocket. This does not necessarily mean the test failed,"
                          " there just might be little activity from endpoint at the moment.")
            print("No mails arrived in allotted time.")
            return
        self.assertIsInstance(item, dict)
        self.assertIsInstance(tb_kills.make_row(item, self.service), tb_kills)

    def test_coroutine_process_json(self):
        asyncio.run_coroutine_threadsafe(self.zk.coroutine_process_json(self.thread_Pool), self.loop)
        self.zk._km_preProcess.sync_q.put_nowait(self.data)
        mail = self.zk._km_postProcess.sync_q.get(block=True, timeout=10)
        self.assertIsInstance(mail, tb_kills)
        self.assertEqual(74647898, mail.kill_id)
        for a in mail.object_attackers + [mail.object_victim]:
            self.assertNotEqual(None, a.object_pilot.character_name)
            self.assertNotEqual(None, a.object_corp.corporation_name)
            if a.object_alliance is not None:
                self.assertNotEqual(None, a.object_alliance.alliance_name)
            if a.object_ship is not None:
                self.assertNotEqual(None, a.object_ship.type_name)
        self.assertNotEqual(None, mail.object_system.name)

    def test_coroutine_filters(self):
        asyncio.run_coroutine_threadsafe(self.zk.coroutine_filters(self.thread_Pool), self.loop)
        mail = tb_kills.make_row(self.data, self.service)
        self.zk._km_postProcess.sync_q.put_nowait(mail)
        self.assertIsInstance(mail, tb_kills)
        time.sleep(.3)
        self.assertTrue(mail in self.service.channel_manager.mock_mails_sent)

    def test_make_queues(self):
        self.assertIsInstance(self.zk._km_preProcess, janus.Queue)
        self.assertIsInstance(self.zk._km_postProcess, janus.Queue)
