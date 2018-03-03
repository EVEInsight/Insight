import asyncio
import traceback

import mysql.connector

import bot.channel_manager.channel


class EntityFeed(object):
    def __init__(self, channel_ob):  # todo add discord channel check
        if not isinstance(channel_ob, bot.channel_manager.channel.d_channel):
            exit()

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
        self.tracking = None
        self.e_vars = {}
        self.load_vars()
        # if self.c_vars['display_statusOnStart']: #todo status add
        #     self.client.loop.create_task(self.command_status())

    def load_vars(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_EntityFeed` WHERE `EntityFeed_channel` = %s;",
                           [self.channel.id])
            self.e_vars = cursor.fetchone()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    async def command_addEntity(self, d_message, message):
        def is_author(m):
            return m.author == d_message.author

        with d_message.channel.typing():
            await d_message.channel.send(
                "{}\nThis tool will assist in adding a target entity to track for the killfeed.\n\n"
                "Please enter the name of the entity you wish to track. This can be a pilot, "
                "corporation, or alliance name.\n".format(d_message.author.mention))
        try:
            author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
        except asyncio.TimeoutError:
            await d_message.channel.send("{}\nSorry, but you took to long to respond".format(d_message.author.mention))
            return
        else:
            for key, val in self.client.en_updates.find(str(author_answer.content)).items():
                print(val)

    async def listen_command(self, d_message, message):
        sub_command = ' '.join((str(message).split()[1:]))
        if d_message.author == self.client.user:
            return
        if await self.client.lookup_command(sub_command, self.client.commands_all['subc_enfeed_addentity']):
            await self.command_addEntity(d_message, sub_command)
        elif await self.client.lookup_command(sub_command, self.client.commands_all['command_allelse']):
            await self.client.command_not_found(d_message)  # todo fix partial command
        else:
            return

    @staticmethod
    async def createNewFeed(channel_ob):
        if not isinstance(channel_ob, bot.channel_manager.channel.d_channel):
            exit()
        else:
            try:
                connection = mysql.connector.connect(**channel_ob.con_.config())
                cursor = connection.cursor(dictionary=True)
                cursor.execute("INSERT IGNORE INTO `discord_EntityFeed` (`EntityFeed_channel`) VALUES (%s);",
                               [channel_ob.c_vars['channel_id']])
                connection.commit()
                await channel_ob.channel.send('Created a new EntityFeed!\nYou must now set up alliances, corps, '
                                              'or pilots to track by running the following command:\n\n'
                                              '"!csettings !enfeed !add_entity"\n')
            except Exception as ex:
                print(ex)
                await channel_ob.channel.send(
                    'Something went wrong went attempting to create a new EntityFeed in the database')
                if connection:
                    connection.rollback()
            finally:
                if connection:
                    connection.close()
