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


class TestZk(DatabaseTesting.DatabaseTesting, AsyncTesting.AsyncTesting):
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

    def test_generate_identifier(self):
        self.tearDown()
        identifier = self.zk.generate_identifier()
        self.assertIsInstance(identifier, str)
        self.assertEqual(8, len(identifier))
        self.assertTrue(os.path.exists("zk_identifier.txt"))
        with open("zk_identifier.txt") as f:
            self.assertEqual(identifier, f.read())

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

    def test_pull_kms_redisq(self):
        asyncio.run_coroutine_threadsafe(self.zk.pull_kms_redisq(), self.loop)
        try:
            item = self.zk._km_preProcess.sync_q.get(block=True, timeout=120)
        except queue.Empty:
            self.fail("Took too long to get a response from websocket. This does not necessarily mean the test failed,"
                      " there just might be little activity from endpoint at the moment.")
        self.assertIsInstance(item, dict)
        self.assertIsInstance(tb_kills.make_row(item, self.service), tb_kills)

    # def test_ws_extract(self): #implied pass if pull_kms_ws passes
    #     self.fail()

    def test_pull_kms_ws(self):
        asyncio.run_coroutine_threadsafe(self.zk.pull_kms_ws(), self.loop)
        try:
            item = self.zk._km_preProcess.sync_q.get(block=True, timeout=120)
        except queue.Empty:
            self.fail("Took too long to get a response from websocket. This does not necessarily mean the test failed,"
                      " there just might be little activity from endpoint at the moment.")
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
