import asyncio
import datetime
import queue
import threading
import time
import traceback

import discord
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
        self.e_vars = {}
        self.run_flag = False
        self.no_tracking_target = True
        self.load_vars()
        self.killQueue = queue.Queue()
        self.postedQueue = queue.Queue()
        self.start_threads()

        if not self.run_flag and not self.no_tracking_target:
            self.client.loop.create_task(self.channel.send(
                'This is an active entityFeed channel with a tracked target however the feed is paused.\nIf you wish to resume it run "!csettings !enfeed !start"'))


    def load_vars(self):
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_EntityFeed` WHERE `EntityFeed_channel` = %s;",
                           [self.channel.id])
            self.e_vars = cursor.fetchone()
            self.run_flag = bool(self.e_vars['is_running'])
            cursor.execute("SELECT * FROM `discord_EntityFeed_tracking` WHERE `EntityFeed_fk` = %s;",
                           [self.channel.id])
            if cursor.fetchone() == None:
                self.no_tracking_target = True
            else:
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

    async def command_saveVars(self):
        self.e_vars['is_running'] = int(self.run_flag)
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            sql = "UPDATE discord_EntityFeed SET {} WHERE EntityFeed_channel=%s".format(
                ', '.join('{}=%s'.format(key) for key in self.e_vars))
            cursor.execute(sql, [str(i) for i in self.e_vars.values()] + [self.e_vars['EntityFeed_channel']])
            connection.commit()
        except Exception as ex:
            print(ex)
            await self.channel.send(
                "Something went wrong when attempting to save EntityFeed variables. Channel variables were not saved.\nCheck that MySQL is correctly running and configured and try again.")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

    def watcher(self):
        pass

    def enqueue_loop(self):
        def exists_in_q(val):
            with self.killQueue.mutex:
                in_kq = val in self.killQueue.queue
            with self.postedQueue.mutex:
                in_pq = val in self.postedQueue.queue
            return (in_kq or in_pq)

        def ignore(km):  # ignore conditions instead of doing everything in sql
            if km['ship_group_id'] == 29:
                if km['totalValue'] < km['pod_isk_floor']:
                    return True
            elif km['ship_category_id'] == 22 and km['ignore_deployable'] == 1:
                return True
            elif km['ship_category_id'] == 65 and km['ignore_citadel'] == 1:
                return True
            elif km['show_loses'] == 0:
                if km['alliance_tracking'] == km['alliance_id']:
                    return True
                if km['corp_tracking'] == km['corp_id']:
                    return True
                if km['pilot_tracking'] == km['pilot_id']:
                    return True
            elif km['show_kills'] == 0:
                if km['alliance_tracking'] is not None:  # null safe compare
                    if km['alliance_tracking'] != km['alliance_id']:
                        return True
                elif km['corp_tracking'] is not None:  # null safe compare
                    if km['corp_tracking'] != km['corp_id']:
                        return True
                elif km['pilot_tracking'] is not None:  # null safe compare
                    if km['pilot_tracking'] != km['pilot_id']:
                        return True
            else:
                return False

        def add_toPost():
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    'SELECT details.*, tracking_config.* FROM ( SELECT * FROM ( SELECT inv_tr.kill_id, tr.EntityFeed_fk from zk_involved as inv_tr, discord_EntityFeed_tracking as tr WHERE EntityFeed_fk = (%s) AND ((tr.alliance_tracking IS NOT NULL AND inv_tr.alliance_id <=> tr.alliance_tracking) or (tr.corp_tracking IS NOT NULL AND inv_tr.corporation_id <=> tr.corp_tracking) or (tr.pilot_tracking IS NOT NULL AND inv_tr.character_id <=> tr.pilot_tracking)) GROUP BY inv_tr.kill_id )inv_in left outer join discord_EntityFeed_posted as post ON inv_in.kill_id = post.kill_id_posted AND post.EntityFeed_posted_to = inv_in.EntityFeed_fk WHERE kill_id_posted iS NULL )final inner join kill_id_victimFB as details on final.kill_id=details.kill_id INNER JOIN discord_EntityFeed_tracking as tracking_config on final.EntityFeed_fk = tracking_config.EntityFeed_fk;',
                    [self.channel.id])  # SelectUnpostedKillWithDetails.sql
                for item in cursor.fetchall():
                    if ignore(item):
                        self.postedQueue.queue.append(item)
                    elif exists_in_q(item):
                        self.postedQueue.queue.append(item)
                    else:
                        self.killQueue.queue.append(item)
            except Exception as ex:
                print(ex)
            finally:
                if connection:
                    connection.close()

        def registerPosted():
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                while not self.postedQueue.empty():
                    cursor.execute(
                        "INSERT IGNORE INTO `discord_EntityFeed_posted`(EntityFeed_posted_to,kill_id_posted,posted_date) VALUES (%s,%s,%s)",
                        [self.channel.id, self.postedQueue.queue.pop()['kill_id'], datetime.datetime.utcnow()])
                connection.commit()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
            finally:
                if connection:
                    connection.close()
        while self.run_flag:
            add_toPost()
            registerPosted()
            time.sleep(20)

    async def async_loop(self):
        def isk_lost_format(val):
            if val >= 1000000000:
                num = float(val / 1000000000)
                return '{:.2f}b'.format(num)
            elif val >= 1000000:
                num = float(val / 1000000)
                return '{:.2f}m'.format(num)
            else:
                num = float(val / 10000)
                return '{:.2f}k'.format(num)

        def en_id(d):
            if d['alliance_tracking'] is not None:
                return d['alliance_tracking']
            elif d['corp_tracking'] is not None:
                return d['corp_tracking']
            elif d['pilot_tracking'] is not None:
                return d['pilot_tracking']
            else:
                return None

        def enIsVictim(id, d):
            if d['pilot_id'] == id or d['corp_id'] == id or d['alliance_id'] == id:
                return True
            else:
                return False

        async def send_message(item):
            mention_everyone = ""
            if enIsVictim(en_id(item), item):
                sidebar_color = 16711680  # red
                kill_or_loss = "Loss"
                if item['totalValue'] >= item['mentionOnLoss_iskFloor']:
                    mention_everyone = "@everyone"
            else:
                sidebar_color = 65299  # green
                kill_or_loss = "Kill"
                if item['totalValue'] >= item['mentionOnKill_iskFloor']:
                    mention_everyone = "@everyone"
            if item['alliance_id'] is not None:
                author_icon_url = "https://imageserver.eveonline.com/Alliance/{}_128.png".format(item['alliance_id'])
            else:
                author_icon_url = "https://imageserver.eveonline.com/Corporation/{}_128.png".format(item['corp_id'])
            minutes_ago = round(
                ((datetime.datetime.utcnow() - item['kill_time']).total_seconds() / 60), 1)
            field_dsc = '```\nName:{p:<10}{p_name}\n' \
                        'Corp:{p:<10}{corp_name}<{corp_ticker}>\n' \
                        'Alliance:{p:<6}{alliance_name}<{alliance_ticker}>\n' \
                        'Damage Taken:{p:<2}{damage_taken}\n' \
                        'Involved:{p:<6}{inv}\n' \
                        'ISK Lost:{p:<6}{isk_loss}\n' \
                        'Time:{p:<10}{min_ago} m/ago```\n' \
                        'https://zkillboard.com/kill/{kill_id}/'.format(p=' ', kill_id=item['kill_id'],
                                                                        p_name=item['pilot_name'],
                                                                        corp_name=item['corp_name'],
                                                                        corp_ticker=item['corp_ticker'],
                                                                        alliance_name=item['alliance_name'],
                                                                        alliance_ticker=item['alliance_ticker'],
                                                                        damage_taken=item['damage_taken'],
                                                                        inv=item['total_involved'],
                                                                        isk_loss=isk_lost_format(item['totalValue']),
                                                                        min_ago=str(minutes_ago))
            embed = discord.Embed(title="```\n```", colour=discord.Colour(sidebar_color),
                                  url="https://zkillboard.com/kill/{}/".format(item['kill_id']),
                                  description='**{ship_name}** destroyed in **[{system_name}]'
                                              '(https://zkillboard.com/system/{system_id}/)** ({region_name})\n\n'
                                              '**[{pilot_name}](https://zkillboard.com/character/{pilot_id}/)** '
                                              '**({corp_name})** lost their **{ship_name}** worth **{loss_value}** '
                                              'ISK to **{total_involved}** pilots **{minutes_ago}** minutes ago.'
                                  .format(ship_name=item['ship_name'], system_name=item['system_name'],
                                          system_id=item['system_id'],
                                          region_name=item['region_name'], pilot_name=item['pilot_name'],
                                          pilot_id=item['pilot_id'], corp_name=item['corp_name'],
                                          loss_value=isk_lost_format(item['totalValue']),
                                          total_involved=item['total_involved'], minutes_ago=str(minutes_ago)),
                                  timestamp=item['kill_time'])
            embed.set_image(url="https://imageserver.eveonline.com/Render/{}_128.png".format(str(item['ship_id'])))
            embed.set_thumbnail(
                url="https://imageserver.eveonline.com/Character/{}_64.jpg".format(str(item['pilot_id'])))
            embed.set_author(name=kill_or_loss,
                             url="https://zkillboard.com/kill/{kill_id}/".format(kill_id=str(item['kill_id'])),
                             icon_url=author_icon_url)

            embed.add_field(name="**Details**",
                            value=field_dsc,
                            inline=False)
            await self.channel.send(content=mention_everyone, embed=embed)
            self.postedQueue.queue.append(item)

        while self.run_flag:
            while not self.killQueue.empty() and self.run_flag:
                await send_message(self.killQueue.queue.pop())
                await asyncio.sleep(5)
            await asyncio.sleep(10)

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

    async def command_addEntity(self, d_message, message):
        def is_author(m):
            return m.author == d_message.author

        async def add_tracking(insert):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                sql = "INSERT INTO discord_EntityFeed_tracking({}) VALUES ({})".format(
                    ', '.join('{}'.format(key) for key in insert),
                    ', '.join('%s' for key in insert))
                cursor.execute(sql, [i for i in insert.values()])
                connection.commit()
                await self.channel.send(
                    "Successfully added a new entity to tracking!\nYou should start seeing feed activity!")
                await self.command_start()
            except Exception as ex:
                print(ex)
                if connection:
                    connection.rollback()
                    connection.close()
            finally:
                if connection:
                    connection.close()

        def find_name(dict):
            for key, val in dict.items():
                if val is not None:
                    for i in val:
                        if 'pilot_name' in i:
                            return i['pilot_name']
                        elif 'corp_name' in i:
                            return i['corp_name']
                        elif 'alliance_name' in i:
                            return i['alliance_name']
            return None

        def find_id_and_db_key(from_d, to_d):
            """takes dict from select system, parses key and appends the correct id to the db_insert dictionary"""
            for key, val in from_d.items():
                if val is not None:
                    for i in val:
                        if 'pilot_id' in i:
                            to_d['pilot_tracking'] = i['pilot_id']
                        elif 'corp_id' in i:
                            to_d['corp_tracking'] = i['corp_id']
                        elif 'alliance_id' in i:
                            to_d['alliance_tracking'] = i['alliance_id']

        async def prompts():
            db_insert_tracking = {'EntityFeed_fk': self.channel.id}
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nThis tool will assist in adding a target entity to track for the killfeed.\n\n"
                    "Please enter the name of the entity you wish to track. This can be a pilot, "
                    "corporation, or alliance name.\n".format(d_message.author.mention))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                entity_select = await self.client.select_entity(self.client.en_updates.find(author_answer.content),
                                                                d_message, author_answer.content)
                find_id_and_db_key(entity_select, db_insert_tracking)
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nDo you wish to track kills participated in by {}?\n\n0 - No\n1 - Yes".format(
                        d_message.author.mention, find_name(entity_select)))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":
                    db_insert_tracking['show_kills'] = 1
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    db_insert_tracking['show_kills'] = 0
                else:
                    await d_message.channel.send(
                        '{}\nYou entered an invalid response.\nResponse must be "1" or "0"'.format(
                            d_message.author.mention))
                    return
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nDo you wish to track losses belonging to {}?\n\n0 - No\n1 - Yes".format(
                        d_message.author.mention, find_name(entity_select)))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":
                    db_insert_tracking['show_loses'] = 1
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    db_insert_tracking['show_loses'] = 0
                else:
                    await d_message.channel.send(
                        '{}\nYou entered an invalid response.\nResponse must be "1" or "0"'.format(
                            d_message.author.mention))
                    return
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nDo you wish to ignore citadel killmails?\n\n0 - No\n1 - Yes".format(d_message.author.mention))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":
                    db_insert_tracking['ignore_citadel'] = 1
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    db_insert_tracking['ignore_citadel'] = 0
                else:
                    await d_message.channel.send(
                        '{}\nYou entered an invalid response.\nResponse must be "1" or "0"'.format(
                            d_message.author.mention))
                    return
            with d_message.channel.typing():
                await d_message.channel.send(
                    "{}\nDo you wish to ignore deployable killmails? (mobile cyno inhib, mobile depot, etc)\n\n0 - No\n1 - Yes".format(
                        d_message.author.mention))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":
                    db_insert_tracking['ignore_deployable'] = 1
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    db_insert_tracking['ignore_deployable'] = 0
                else:
                    await d_message.channel.send(
                        '{}\nYou entered an invalid response.\nResponse must be "1" or "0"'.format(
                            d_message.author.mention))
                    return
            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nPlease enter an ISK value floor for POD killmails.\n\nOnly PODS above this ISK value will be '
                    'posted to the channel.\n\nIf you wish to ignore all pods regardless of '
                    'value enter "none"\nIf you wish to track all pods enter a low value such as "0"'.format(
                        d_message.author.mention))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                try:
                    floor = float(author_answer.content)
                    db_insert_tracking['pod_isk_floor'] = floor
                except ValueError:
                    pass
            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nYou can have the bot mention everyone in channel if a streamed kill belonging to {} excedes a set ISK value.\n\n'
                    'Enter an ISK value floor. All kills (not losses) above this ISK value will ping and mention everyone in channel.\n'
                    'If you do not wish to use this feature enter "none".'.format(d_message.author.mention,
                                                                                  find_name(entity_select)))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                try:
                    floor = float(author_answer.content)
                    db_insert_tracking['mentionOnKill_iskFloor'] = floor
                except ValueError:
                    pass
            with d_message.channel.typing():
                await d_message.channel.send(
                    '{}\nYou can have the bot mention everyone in channel if a streamed loss belonging to {} excedes a set ISK value.\n\n'
                    'Enter an ISK value floor. All losses (not kills) above this ISK value will ping and mention everyone in channel.\n'
                    'If you do not wish to use this feature enter "none".'.format(d_message.author.mention,
                                                                                  find_name(entity_select)))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                try:
                    floor = float(author_answer.content)
                    db_insert_tracking['mentionOnLoss_iskFloor'] = floor
                except ValueError:
                    pass
            with d_message.channel.typing():
                statement_list = []
                statement_list.append(str("Entity Name: {}".format(find_name(entity_select))))
                statement_list.append(
                    str("Show Kills: {}".format(str("True" if db_insert_tracking['show_kills'] == 1 else "False"))))
                statement_list.append(
                    str("Show Losses: {}".format(str("True" if db_insert_tracking['show_loses'] == 1 else "False"))))
                statement_list.append(
                    str("Ignore Citadels: {}".format(
                        str("True" if db_insert_tracking['ignore_citadel'] == 1 else "False"))))
                statement_list.append(
                    str("Ignore Deployable: {}".format(
                        str("True" if db_insert_tracking['ignore_deployable'] == 1 else "False"))))
                statement_list.append(
                    str("Pod ISK Floor (none if not tracking pods): {}".format(str(
                        "none" if 'pod_isk_floor' not in db_insert_tracking else db_insert_tracking['pod_isk_floor']))))
                statement_list.append(
                    str("Mention Kill Above ISK Floor (none if not mentioning): {}".format(str(
                        "none" if 'mentionOnKill_iskFloor' not in db_insert_tracking else db_insert_tracking[
                            'mentionOnKill_iskFloor']))))
                statement_list.append(
                    str("Mention Loss Above ISK Floor (none if not mentioning): {}".format(str(
                        "none" if 'mentionOnLoss_iskFloor' not in db_insert_tracking else db_insert_tracking[
                            'mentionOnLoss_iskFloor']))))
                st_str = ""
                for i in statement_list:
                    st_str += str(i + '\n')
                await d_message.channel.send(
                    '{}\n{}\n\nIf the above values are correct and you wish to track based on these settings please confirm by accepting\n\n'
                    '0 - Decline Addition\n'
                    '1 - Accept Addition'.format(d_message.author.mention, st_str))
            try:
                author_answer = await self.client.wait_for('message', timeout=30, check=is_author)
            except asyncio.TimeoutError:
                await d_message.channel.send(
                    "{}\nSorry, but you took to long to respond".format(d_message.author.mention))
                return
            else:
                if str(author_answer.content) == "1" or str(author_answer.content) == "yes":
                    await add_tracking(db_insert_tracking)
                elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                    await d_message.channel.send('{}\nChanges declined. No changes were made to the entity feed'.format(
                        d_message.author.mention))
                    return
                else:
                    await d_message.channel.send(
                        '{}\nYou entered an invalid response.\nResponse must be "1" or "0"'.format(
                            d_message.author.mention))
                    return

        await prompts()

    async def command_start(self):
        if self.run_flag == True:
            await self.channel.send(
                'The entityFeed is already running. If you wish to pause it run\n"!csettings !enfeed !stop"')
        else:
            self.run_flag = True
            await self.command_saveVars()
            await self.channel.send(
                'The entityFeed is now running. If you wish to pause it run\n"!csettings !enfeed !stop" ')
            self.setup()

    async def command_stop(self):
        if self.run_flag == False:
            await self.channel.send(
                'The entityFeed is already paused. If you wish to start it run\n"!csettings !enfeed !start"')
        else:
            self.run_flag = False
            await self.command_saveVars()
            await self.channel.send(
                'The entityFeed is paused. If you wish to start it run\n"!csettings !enfeed !start" ')
            self.setup()
    async def listen_command(self, d_message, message):
        sub_command = ' '.join((str(message).split()[1:]))
        if d_message.author == self.client.user:
            return
        if await self.client.lookup_command(sub_command, self.client.commands_all['subc_enfeed_addentity']):
            await self.command_addEntity(d_message, sub_command)
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_start']):
            await self.command_start()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_stop']):
            await self.command_stop()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['command_allelse']):
            await self.client.command_not_found(d_message)  # todo fix partial commands
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
