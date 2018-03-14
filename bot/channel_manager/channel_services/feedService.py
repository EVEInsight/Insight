import asyncio
import datetime
import queue
import threading
import time
import traceback

import discord
import mysql.connector

import bot.channel_manager.channel
from abc import ABCMeta, abstractmethod



class feedService(metaclass=ABCMeta):
    def __init__(self, channel_ob):  # todo add discord channel check
        assert (isinstance(channel_ob, bot.channel_manager.channel.d_channel))
        assert (self != feedService)  # cant instantiate superclass

        # object instances
        self.manager = channel_ob.manager
        self.channel = channel_ob.channel
        self.con_ = self.manager.con_
        self.config_file = self.manager.config_file
        self.arguments = self.manager.arguments
        self.client = self.manager.client

        # vars
        self.setup()

    def setup(self):
        self.feedConfig = {}
        self.run_flag = False
        self.no_tracking_target = True
        self.load_vars()
        self.killQueue = queue.Queue()
        self.postedQueue = queue.Queue()
        self.start_threads()

        if not self.run_flag and not self.no_tracking_target:
            self.client.loop.create_task(self.channel.send(
                'This is an active {} channel with a tracked config however the feed is paused.\nIf you wish to resume it run "!csettings {} !start"'.format(
                    self.feedName(), self.feedCommand())))

    @abstractmethod
    def load_vars(self):
        pass

    async def command_saveVars(self):
        self.feedConfig['is_running'] = int(self.run_flag)
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            sql = "UPDATE {} SET {} WHERE {}=%s".format(self.sql_saveVars()['table'],
                                                        ', '.join('{}=%s'.format(key) for key in self.feedConfig),
                                                        self.sql_saveVars()['col'])
            cursor.execute(sql, [str(i) for i in self.feedConfig.values()] + [self.channel.id])
            connection.commit()
        except Exception as ex:
            print(ex)
            await self.channel.send(
                "Something went wrong when attempting to save {} variables. Channel variables were not saved.\nCheck that MySQL is correctly running and configured and try again.".format(
                    self.feedName()))
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

    def watcher(self):
        pass

    @abstractmethod
    def enqueue_loop(self):
        """loop to fetch and parse information that should be posted to the channel"""

    @abstractmethod
    async def async_loop(self):
        """async loop that goes through kills to be posted and sends them to channel"""

    def start_threads(self):
        if not self.no_tracking_target:
            self.thread_watcher = threading.Thread(target=self.watcher)
            self.thread_watcher.start()
            self.enqueue_bg = threading.Thread(target=self.enqueue_loop)
            self.enqueue_bg.start()
            self.dequeue_bg = self.client.loop.create_task(self.async_loop())
        else:
            self.client.loop.create_task(self.channel.send('\n\nThere are currently no tracked entities '
                                                           'set for this channel. \nYou must create a tracking '
                                                           'target by running "!csettings !enfeed !add_entity"\nIf '
                                                           'you created an entityFeed in this channel by error, run the'
                                                           ' command "!csettings !reset" to remove this message'))

    async def command_start(self):
        if self.run_flag == True:
            await self.channel.send(
                'The {} is already running. If you wish to pause it run\n"!csettings {} !stop"'.format(self.feedName(),
                                                                                                       self.feedCommand()))
        else:
            self.run_flag = True
            await self.command_saveVars()
            await self.channel.send(
                'The {} is now running. If you wish to pause it run\n"!csettings {} !stop" '.format(self.feedName(),
                                                                                                    self.feedCommand()))
            self.setup()

    async def command_stop(self):
        if self.run_flag == False:
            await self.channel.send(
                'The {} is already paused. If you wish to start it run\n"!csettings {} !start"'.format(self.feedName(),
                                                                                                       self.feedCommand()))
        else:
            self.run_flag = False
            await self.command_saveVars()
            await self.channel.send(
                'The {} is paused. If you wish to start it run\n"!csettings {} !start" '.format(self.feedName(),
                                                                                                self.feedCommand()))
            self.setup()

    async def command_lock(self):
        """lock the channel threads on an exception"""
        self.run_flag = False

    @abstractmethod
    async def listen_command(self, d_message, message):
        """listen command must override with specific command paths for type of feed"""
        pass

    def feedName(self):
        """Returns the name of the feed or object name"""
        return str(self.__class__.__name__)

    @abstractmethod
    def sql_saveVars(self):
        """UPDATE {} SET {} WHERE {} for function command_saveVars"""
        pass

    @abstractmethod
    def feedCommand(self):
        pass

    @staticmethod
    @abstractmethod
    async def createNewFeed(channel_ob, d_message):
        pass

    @staticmethod
    async def ask_question(question, d_message, client, timeout=30, embed=None):
        assert (isinstance(client, discord.Client))
        assert (isinstance(question, str))
        assert (isinstance(d_message, discord.Message))
        assert (isinstance(timeout, int))

        def is_author(m):
            return m.author == d_message.author

        async def timeout_message(d_message):
            await d_message.channel.send(
                "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
            raise asyncio.TimeoutError("Waiting for user response timeout")

        with d_message.channel.typing():
            await d_message.channel.send('{}'.format(question), embed=embed)
        try:
            return await client.wait_for('message', timeout=timeout, check=is_author)
        except asyncio.TimeoutError:
            await timeout_message(d_message)
