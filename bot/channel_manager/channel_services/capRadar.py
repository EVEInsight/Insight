from bot.channel_manager.channel_services.feedService import *


class capRadar(feedService):
    def __init__(self, channel_ob):
        super(capRadar, self).__init__(channel_ob=channel_ob)

    def load_vars(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_CapRadar` WHERE `channel` = %s;",
                           [self.channel.id])
            self.feedConfig = cursor.fetchone()
            if self.feedConfig is not None:
                self.run_flag = bool(self.feedConfig['is_running'])
                self.no_tracking_target = False
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    def enqueue_loop(self):
        raise NotImplementedError

    async def async_loop(self):
        raise NotImplementedError

    async def listen_command(self, d_message, message):
        raise NotImplementedError

    def sql_saveVars(self):
        return {'table': 'discord_CapRadar', 'col': 'channel'}

    def feedCommand(self):
        return str((self.client.commands_all['subc_channel_capradar'])[0])

    @staticmethod
    async def createNewFeed(channel_ob, d_message):
        """prompts and inserts settings before creating the object as object is loaded from database"""

        def insert_db(item):
            try:
                connection = mysql.connector.connect(**channel_ob.con_.config())
                cursor = connection.cursor(dictionary=True)
                sql = "INSERT INTO `discord_CapRadar`({}) VALUES ({})".format(
                    ', '.join('{}'.format(key) for key in insert),
                    ', '.join('%s' for key in insert))
                cursor.execute(sql, [i for i in insert.values()])
                connection.commit()
            except Exception as ex:
                if connection:
                    connection.rollback()
                    connection.close()
                raise Exception("Something went wrong when saving the new config to MySQL database.")
            finally:
                if connection:
                    connection.close()

        if not isinstance(channel_ob, bot.channel_manager.channel.d_channel):
            exit()
        else:
            try:
                insert = (await capRadar.ask_settings(channel_ob, d_message))
                insert_db(insert)
                await channel_ob.channel.send('Successfully created a new radar feed in this channel.\n'
                                              'You will now see active targets according to your specified settings.\n\n'
                                              'You should now run the command "!csettings !capRadar !ignore" to import an ignore list.\n'
                                              'The ignore list allows your capRadar feed to ignore friendly targets while showing only the hostile ones.')
            except Exception as ex:
                print(ex)
                await channel_ob.channel.send(
                    'Something went wrong when attempting to create a new capRadar Feed\nException raised: "{}"'.format(
                        str(ex)))

    @staticmethod
    async def ask_settings(ch, d_message):
        """prompts user for settings and returns a dictionary for setting insertion into the database"""

        def is_author(m):
            return m.author == d_message.author

        async def timeout_message():
            await d_message.channel.send(
                "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
            raise asyncio.TimeoutError("Waiting for user response timeout")

        async def response():
            try:
                return (await ch.client.wait_for('message', timeout=30, check=is_author))
            except asyncio.TimeoutError:
                await timeout_message()

        async def prompt():
            db_insert_tracking = {'channel': ch.channel.id}
            system_name = None
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nThis tool will assist in setting up a capRadar feed.\n\n"
                    "The capRadar alerts you of capital, super, and black ops activity within jump range of a specified system.\n\n"
                    "First, enter the name of your base system you wish to track capitals in range of:\n".format(
                        d_message.author.mention))
            author_answer = await response()
            system = await ch.client.select_system(ch.client.m_systems.find(author_answer.content), d_message,
                                                   author_answer.content)
            db_insert_tracking['system_base'] = system['system_id']
            system_name = system['system_name']

            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nPlease specify the maximum capital jump range you wish to track capitals in LYs from your base system. Kills outside of this jump range will not be posted to the channel.\n\n'
                    'Example: If you wish to only show capitals active within black ops direct jump range of your base system you would enter "8"\n\n\nMax Radar Range in LYs: '.format(
                        d_message.author.mention))
            author_answer = await response()
            try:
                db_insert_tracking['maxLY_fromBase'] = float(author_answer.content)
            except ValueError:
                raise Exception("{} is not a number".format(author_answer.content))

            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nDo you wish to track supers in this capRadar feed?\n\n'
                    'This will track supercarriers, titans, and faction supers/titans\n\nPlease select an option by entering the corresponding number\n\n\n'
                    '0 - No\n'
                    '1 - Yes\n\n'
                    'Your response: '.format(d_message.author.mention))
            author_answer = await response()
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_supers'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_supers'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nDo you wish to track normal capitals in this capRadar feed?\n\n'
                    'This will track carriers, force auxiliary carriers, and dreadnoughts.\n\n'
                    'Note: If you answered yes to tracking supers in the previous prompt and select yes to this prompt you will track both normal capitals in addition to supers.\n\n'
                    'Please select an option by entering the corresponding number\n\n\n'
                    '0 - No\n'
                    '1 - Yes\n\n'
                    'Your response: '.format(d_message.author.mention))
            author_answer = await response()
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_capitals'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_capitals'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nDo you wish to track black ops battleships in this capRadar feed?\n\n'
                    'This will track black ops battleships\n\nPlease select an option by entering the corresponding number\n\n\n'
                    '0 - No\n'
                    '1 - Yes\n\n'
                    'Your response: '.format(d_message.author.mention))
            author_answer = await response()
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_blops'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_blops'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            if db_insert_tracking['track_supers'] == 1:
                with d_message.channel.typing():
                    await d_message.channel.send(
                        '{}\nOn detected supercapital activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                        'Note: if you select disable, supercapital activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                        'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                        'Please select an option by entering the corresponding number\n\n\n'
                        '0 - disable this feature\n'
                        '1 - @ here\n'
                        '2 - @ everyone\n\n'
                        'Your response: '.format(d_message.author.mention))
                author_answer = await response()
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['super_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['super_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

            if db_insert_tracking['track_capitals'] == 1:
                with d_message.channel.typing():
                    await d_message.channel.send(
                        '{}\nOn detected capital activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                        'Note: if you select disable, capital activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                        'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                        'Please select an option by entering the corresponding number\n\n\n'
                        '0 - disable this feature\n'
                        '1 - @ here\n'
                        '2 - @ everyone\n\n'
                        'Your response: '.format(d_message.author.mention))
                author_answer = await response()
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['capital_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['capital_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

            if db_insert_tracking['track_blops'] == 1:
                with d_message.channel.typing():
                    await d_message.channel.send(
                        '{}\nOn detected blops activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                        'Note: if you select disable, blops activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                        'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                        'Please select an option by entering the corresponding number\n\n\n'
                        '0 - disable this feature\n'
                        '1 - @ here\n'
                        '2 - @ everyone\n\n'
                        'Your response: '.format(d_message.author.mention))
                author_answer = await response()
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['blops_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['blops_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

            with d_message.channel.typing():
                statement_list = []
                statement_list.append(str("Base System Name: {}".format(system_name)))
                statement_list.append(
                    str("Radar Max LY range from Base: {}".format(str(db_insert_tracking['maxLY_fromBase']))))
                statement_list.append(
                    str("Track Supers (titans/supercarriers): {}".format(
                        str("True" if db_insert_tracking['track_supers'] == 1 else "False"))))
                statement_list.append(
                    str("Track Capitals (carriers/faxes/dreads): {}".format(
                        str("True" if db_insert_tracking['track_capitals'] == 1 else "False"))))
                statement_list.append(
                    str("Track Blops (blops battleships): {}".format(
                        str("True" if db_insert_tracking['track_blops'] == 1 else "False"))))
                statement_list.append(
                    str("Notification method on super activity: {}".format(str(
                        "disabled" if 'super_notification' not in db_insert_tracking else str(db_insert_tracking[
                                                                                                  'super_notification']).strip(
                            '@')))))
                statement_list.append(
                    str("Notification method on capital activity: {}".format(str(
                        "disabled" if 'capital_notification' not in db_insert_tracking else str(db_insert_tracking[
                                                                                                    'capital_notification']).strip(
                            '@')))))
                statement_list.append(
                    str("Notification method on black ops battleship activity: {}".format(str(
                        "disabled" if 'blops_notification' not in db_insert_tracking else str(db_insert_tracking[
                                                                                                  'blops_notification']).strip(
                            '@')))))
                st_str = ""
                for i in statement_list:
                    st_str += str(i + '\n')
                await d_message.channel.send(
                    '{}\n{}\n\nIf the above values are correct and you wish to initiate radar based on these settings please confirm by accepting\n\n'
                    '0 - Decline Addition\n'
                    '1 - Accept Addition'.format(d_message.author.mention, st_str))
                author_answer = await response()
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                    return db_insert_tracking
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    raise Exception("User declined radar settings")
                else:
                    raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

        return (await prompt())
