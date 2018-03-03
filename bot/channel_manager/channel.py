import asyncio
import traceback

import mysql.connector

import bot.channel_manager.channel_manager
from bot.channel_manager.channel_services.entityFeed import EntityFeed


class d_channel(object):
    def __init__(self, channel_manager_instance, channel_instance):
        if not isinstance(channel_manager_instance, bot.channel_manager.channel_manager.channel_manager):
            exit()

        # object instances
        self.manager = channel_manager_instance
        self.channel = channel_instance
        self.con_ = self.manager.con_
        self.config_file = self.manager.config_file
        self.arguments = self.manager.arguments
        self.client = self.manager.client

        # channel vars
        self.setup()

    def setup(self):
        self.c_vars = {}
        self.enFeed = self.load_enFeed()
        self.db_create_channel()
        self.load_vars()
        if self.c_vars['display_statusOnStart']:
            self.client.loop.create_task(self.command_status())

    def db_create_channel(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT IGNORE INTO `discord_channels` (`channel_id`) VALUES (%s);",
                           [self.channel.id])
            cursor.execute("UPDATE `discord_channels` SET `channel_name` = %s WHERE `channel_id` = %s",
                           [self.channel.name, self.channel.id])
            connection.commit()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

    def load_enFeed(self):
        enFeed = None
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_EntityFeed` WHERE `EntityFeed_channel` = %s;",
                           [self.channel.id])
            resp = cursor.fetchone()
            if resp is None:
                enFeed = None
            else:
                enFeed = EntityFeed(self)
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()
            return enFeed

    def load_vars(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_channels` WHERE `channel_id` = %s;",
                           [self.channel.id])
            self.c_vars = cursor.fetchone()
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    async def command_saveVars(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            sql = "UPDATE discord_channels SET {} WHERE channel_id=%s".format(
                ', '.join('{}=%s'.format(key) for key in self.c_vars))
            cursor.execute(sql, [str(i) for i in self.c_vars.values()] + [self.c_vars['channel_id']])
            connection.commit()
            await self.channel.send("Channel variables were saved successfully!")
        except Exception as ex:
            print(ex)
            await self.channel.send(
                "Something went wrong when attempting to save channel variables. Channel variables were not saved.\nCheck that MySQL is correctly running and configured and try again.")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

    async def command_status(self):
        print_str = "Channel Status Information\n\nChannel Name: {}\nDisplay_StatusOnStart: {}".format(
            self.c_vars['channel_name'], self.c_vars['display_statusOnStart'])
        await self.channel.send(print_str)

    async def command_ChangeStatus(self, d_message, message):
        items = (str(message).split()[1:])
        if len(items) == 0:
            await self.channel.send(
                "{}You must provide a boolean value for the switch statusOnStart.\nExample !csettings !config_status 1 to change the value to true".format(
                    d_message.author.mention))
        else:
            if items[0] == "1" or items[0] == "true":
                self.c_vars['display_statusOnStart'] = 1
            elif items[0] == "0" or items[0] == "false":
                self.c_vars['display_statusOnStart'] = 0
            await self.command_saveVars()

    async def command_reset(self, d_message, message):
        def reset():
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                cursor.execute('DELETE FROM discord_channels WHERE channel_id = %s', [self.c_vars['channel_id']])
                connection.commit()
                self.setup()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
            finally:
                if connection:
                    connection.close()

        def reset_check(m):
            return m.author == d_message.author

        with d_message.channel.typing():
            await d_message.channel.send('{}\nYou are about to reset Insight settings for this channel.\n'
                                         'All feeds or customized settings for EVE Insight will be cleared for this channel.'
                                         '\nTo confirm you wish to reset the channel type "reset" without '
                                         'quotes.'.format(d_message.author.mention))
        try:
            resp = await self.client.wait_for('message', timeout=30, check=reset_check)
        except asyncio.TimeoutError:
            await d_message.channel.send("{}\nSorry, but you took to long to respond".format(d_message.author.mention))
            raise TimeoutError("response timeout")
        else:
            if str(resp.content) == "reset":
                await self.channel.send('Resetting the channel')
                reset()
                await self.channel.send('Successfully reset the channel!')
            else:
                await self.channel.send(
                    'Error: You must enter "reset" to reset the channel. Channel settings remain unchanged.')

    async def command_to_entityFeed(self, d_message, message_str):
        sub_command = ' '.join((str(message_str).split()[1:]))
        if isinstance(self.enFeed, EntityFeed):
            await self.enFeed.listen_command(d_message, message_str)
        else:
            if await self.client.lookup_command(sub_command, self.client.commands_all['subc_enfeed_create']):
                if self.enFeed is not None:
                    await self.channel.send('Error: An EntityFeed already exists for this channel.\nYou can '
                                            'delete the currently running EntityFeed by '
                                            'running\n"!csettings !enfeed !reset"')
                else:
                    await EntityFeed.createNewFeed(self)
            else:
                await d_message.channel.send('{}\nThere is no entity killfeed tracker configured for this channel.\n'
                                             'If you wish to create one, type "!csettings '
                                             '!entityFeed !create'.format(d_message.author.mention))

    async def listen_command(self, message):
        sub_command = ' '.join((str(message.content).split()[1:]))
        if message.author == self.client.user:
            return
        if await self.client.lookup_command(sub_command, self.client.commands_all['subc_channel_status']):
            await self.command_status()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_channel_save']):
            await self.command_saveVars()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_channel_statusonstart']):
            await self.command_ChangeStatus(message, sub_command)
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_channel_reset']):
            await self.command_reset(message, sub_command)
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_channel_entity']):
            await self.command_to_entityFeed(message, sub_command)
        elif await self.client.lookup_command(message.content, self.client.commands_all['command_allelse']):
            await self.client.command_not_found(message)  # todo custom fix
        else:
            return
