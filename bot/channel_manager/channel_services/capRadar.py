from bot.channel_manager.channel_services.feedService import *


class capRadar(feedService):
    def __init__(self, channel_ob):
        super(capRadar, self).__init__(channel_ob=channel_ob)

    def load_vars(self):
        self.load_ignores()
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM `discord_CapRadar` WHERE `channel` = %s;",
                           [self.channel.id])
            self.feedConfig = cursor.fetchone()
            if self.feedConfig is not None:
                self.run_flag = bool(self.feedConfig['is_running'])
                self.no_tracking_target = False
                self.base_system = self.client.m_systems.system_by_id(self.feedConfig['system_base'])
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            if connection:
                connection.rollback()
            raise mysql.connector.DatabaseError
        finally:
            if connection:
                connection.close()

    def load_ignores(self):
        self.ignores = {'pilots': [], 'corps': [], 'alliances': []}
        try:
            connection = mysql.connector.connect(**self.con_.config())
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT pilot_id FROM `discord_CapRadar_ignore_pilots` WHERE `channel_cr` = %s;",
                           [self.channel.id])
            self.ignores['pilots'] = [i["pilot_id"] for i in cursor.fetchall()]
            cursor.execute("SELECT corp_id FROM `discord_CapRadar_ignore_corps` WHERE `channel_cr` = %s;",
                           [self.channel.id])
            self.ignores['corps'] = [i["corp_id"] for i in cursor.fetchall()]
            cursor.execute("SELECT alliance_id FROM `discord_CapRadar_ignore_alliances` WHERE `channel_cr` = %s;",
                           [self.channel.id])
            self.ignores['alliances'] = [i["alliance_id"] for i in cursor.fetchall()]
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
        def exists_in_q(val):
            with self.killQueue.mutex:
                kq = list(self.killQueue.queue)
            with self.postedQueue.mutex:
                pq = list(self.postedQueue.queue)

            if val['kill_id'] in [i['kill_id'] for i in kq]:
                return True
            elif val['kill_id'] in [i['kill_id'] for i in pq]:
                return True
            else:
                return False

        def ignore_parse(km):
            attackers = []
            for a in km['attackers']:
                if a['alliance_id'] in self.ignores['alliances'] or a['corp_id'] in self.ignores['corps'] or a[
                    'pilot_id'] in self.ignores['pilots']:
                    continue
                if self.feedConfig['track_supers'] == 0 and self.cap_info.is_super(a['group_id']):
                    continue
                if self.feedConfig['track_capitals'] == 0 and self.cap_info.is_capital(a['group_id']):
                    continue
                if self.feedConfig['track_blops'] == 0 and self.cap_info.is_blops(a['group_id']):
                    continue
                attackers.append(a)
            attackers.sort(key=lambda at: self.cap_info.groups_by_value().index(at['group_id']))
            if len(attackers) != 0:
                km['highest_groupName'] = attackers[0]['group_name']
                km['highest_shipID'] = attackers[0]['ship_id']
                if self.cap_info.is_super(attackers[0]['group_id']):
                    km['mention'] = self.feedConfig['super_notification']
                elif self.cap_info.is_capital(attackers[0]['group_id']):
                    km['mention'] = self.feedConfig['capital_notification']
                elif self.cap_info.is_blops(attackers[0]['group_id']):
                    km['mention'] = self.feedConfig['blops_notification']
                else:
                    km['mention'] = None
            km['attackers'] = attackers
            return km

        def add_toPost():
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    'SELECT kill_id, system_id FROM kills_inv_SuperOrCap120M AS all_k LEFT OUTER JOIN discord_CapRadar_posted AS posted ON all_k.kill_id = posted.kill_id_posted AND (%s) = posted.CapRadar_posted_to WHERE kill_id_posted IS NULL;',
                    [self.channel.id])
                kills_all = cursor.fetchall()
                for id in kills_all:
                    km = {'kill_id': id['kill_id'],
                          'ly_range': self.client.m_systems.ly_range(self.feedConfig['system_base'], id['system_id'],
                                                                     id_only_mode=True), 'target': None,
                          'attackers': [], 'mention': None,
                          'highest_groupName': None, 'highest_shipID': None}
                    if km['ly_range'] > self.feedConfig['maxLY_fromBase']:
                        self.postedQueue.queue.append(km)
                        continue
                    elif exists_in_q(km):
                        self.postedQueue.queue.append(km)
                        continue
                    else:
                        cursor.execute(
                            'SELECT pilot_id, pilot_name, corp_id, corp_name, corp_ticker, iv.alliance_id, alliance_name, ticker AS alliance_ticker, type_id AS ship_id, type_name AS ship_name, group_id, group_name FROM zk_involved AS iv INNER JOIN item_types ON iv.ship_type_id = item_types.type_id INNER JOIN item_groups ON item_types.group_id_fk = item_groups.group_id INNER JOIN item_category ON item_groups.item_category_fk = item_category.category_id INNER JOIN zk_kills AS k ON iv.kill_id = k.killmail_id INNER JOIN systems AS sy ON k.system_id = sy.system_id INNER JOIN constellations AS con ON sy.constellation_id_fk = con.constellation_id INNER JOIN regions AS rg ON con.region_id_fk = rg.region_id LEFT JOIN pilots ON iv.character_id = pilots.pilot_id LEFT JOIN corps ON iv.corporation_id = corps.corp_id LEFT JOIN alliances ON iv.alliance_id = alliances.alliance_id WHERE kill_id = (%s) AND ( group_id <=> 659 OR group_id <=> 30 OR group_id <=> 485 OR group_id <=> 547 OR group_id <=> 1538 OR group_id <=> 883 OR group_id <=> 898) AND NOT is_victim;',
                            [id['kill_id']])
                        km['attackers'] = cursor.fetchall()
                        cursor.execute('SELECT * FROM `kill_id_victimFB` WHERE 	kill_id = (%s)',
                                       [id['kill_id']])
                        km['target'] = cursor.fetchone()
                        km = ignore_parse(km)
                        if len(km['attackers']) == 0:
                            self.postedQueue.queue.append(km)
                            continue
                        else:
                            self.killQueue.queue.append(km)
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
                        "INSERT IGNORE INTO `discord_CapRadar_posted`(CapRadar_posted_to,kill_id_posted,posted_date) VALUES (%s,%s,%s)",
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
            time.sleep(5)

    async def async_loop(self):
        async def send_message(item):
            me_inv = item['attackers'][0]  # most expensive involved attacker by ship
            target = item['target']
            m_ago = str(round(((datetime.datetime.utcnow() - target['kill_time']).total_seconds() / 60), 1))
            kill_id = item['kill_id']
            kill_url = "https://zkillboard.com/kill/{}/".format(str(kill_id))
            link_aliCorp = "https://imageserver.eveonline.com/Alliance/{}_128.png".format(me_inv['alliance_id']) if \
            me_inv['alliance_id'] is not None else "https://imageserver.eveonline.com/Corporation/{}_128.png".format(
                me_inv['corp_id'])
            str_An = "{gName} activity {ly:.2f} LYs away from {b_s}".format(
                gName=item['highest_groupName'],
                ly=item['ly_range'],
                b_s=self.base_system['system_name'],
            )
            str_content = "{m} {gName} activity in {sName}({rName}) {ly_r:.2f} LYs from {b_s} {mago} m/ago".format(
                m=str(item['mention'] if item['mention'] is not None else ""),
                gName=item['highest_groupName'],
                sName=item['target']['system_name'],
                rName=item['target']['region_name'],
                ly_r=(item['ly_range']),
                b_s=self.base_system['system_name'],
                mago=m_ago)
            str_tDesc = "**{v_s}** destroyed in [**{sN}**]({dl_l})({rN}) **{mago}** minutes ago.\n\n*Involving **[{me_n}]({p_l})({me_c}){me_ali}** in **{me_sN}** {inv}*".format(
                v_s=item['target']['ship_name'],
                sN=item['target']['system_name'],
                dl_l="http://evemaps.dotlan.net/system/{}".format(target['system_name']),
                rN=item['target']['region_name'],
                mago=m_ago,
                me_n=me_inv['pilot_name'],
                p_l="https://zkillboard.com/character/{}/".format(me_inv['pilot_id']),
                me_c=me_inv['corp_name'],
                me_ali=str("<{}>".format(me_inv['alliance_ticker'])) if me_inv['alliance_ticker'] is not None else " ",
                me_sN=me_inv['ship_name'],
                inv="flying **solo.**" if target['total_involved'] == 1 else "and **{}** others".format(
                    str(target['total_involved'] - 1))
            )
            inv_ship_t = "{} of {} attackers flying in tracked ships".format(str(len(item['attackers'])),
                                                                             str(target['total_involved']))
            ships_count = {}
            for ship_inv in item['attackers']:
                if ship_inv['ship_name'] not in ships_count:
                    ships_count[ship_inv['ship_name']] = 1
                else:
                    ships_count[ship_inv['ship_name']] += 1
            ship_str = ""
            for ship, count in ships_count.items():
                ship_str += "{s:<20} {c}\n".format(s=ship, c=str(count))
            dr_str = ""
            mids = int(math.floor(item['ly_range'] / float((self.config_file['eve_settings']['super_range_5']))))
            dr_str += "[```{type:<20} {no_mids}```]({dl_link})".format(
                type="Titans/Supers",
                no_mids="{} mids".format(str(mids)) if mids != 0 else "direct range",
                dl_link="http://evemaps.dotlan.net/jump/Aeon,555/{b_s}:{t_s}".format(
                    b_s=self.base_system['system_name'],
                    t_s=target['system_name']
                )
            )
            mids = int(math.floor(item['ly_range'] / float((self.config_file['eve_settings']['carrier_range_5']))))
            dr_str += "[```{type:<20} {no_mids}```]({dl_link})".format(
                type="Carriers/Dreads/FAX",
                no_mids="{} mids".format(str(mids)) if mids != 0 else "direct range",
                dl_link="http://evemaps.dotlan.net/jump/Archon,555/{b_s}:{t_s}".format(
                    b_s=self.base_system['system_name'],
                    t_s=target['system_name']
                )
            )
            mids = int(math.floor(item['ly_range'] / float((self.config_file['eve_settings']['blops_range_5']))))
            dr_str += "[```{type:<20} {no_mids}```]({dl_link})".format(
                type="Blops",
                no_mids="{} mids".format(str(mids)) if mids != 0 else "direct range",
                dl_link="http://evemaps.dotlan.net/jump/Redeemer,555/{b_s}:{t_s}".format(
                    b_s=self.base_system['system_name'],
                    t_s=target['system_name']
                )
            )
            gates = None  # todo gate counter
            dr_str += "[```{type:<20}```]({dl_link})".format(
                type="Gates",
                # no_mids="{} mids".format(str(mids)) if mids != 0 else "direct range",
                dl_link="http://evemaps.dotlan.net/route/{b_s}:{t_s}".format(
                    b_s=self.base_system['system_name'],
                    t_s=target['system_name']
                )
            )
            dr_str += "\n**{}**".format(kill_url)

            embed = discord.Embed(title=" ", colour=discord.Colour(0x691f5b),
                                  url=kill_url,
                                  description=str_tDesc,
                                  timestamp=item['target']['kill_time'])
            embed.set_image(
                url="https://imageserver.eveonline.com/Render/{}_128.png".format(str(item['highest_shipID'])))
            embed.set_thumbnail(url=link_aliCorp)
            embed.set_author(name=str_An, url=kill_url)  # todo readd icon
            # icon_url=None)
            embed.add_field(name=inv_ship_t, value="```{}```".format(ship_str), inline=False)
            embed.add_field(name="Routes from {} (clickable links)".format(self.base_system['system_name']),
                            value=dr_str,
                            inline=False)
            try:
                await self.channel.send(content=str_content, embed=embed)
                self.postedQueue.queue.append(item)
            except discord.Forbidden as ex:
                await self.command_lock()  # disable the thread to save resources if we cant post to it

        while self.run_flag:
            while not self.killQueue.empty() and self.run_flag:
                try:
                    await send_message(self.killQueue.queue.pop())
                except Exception as ex:
                    print(ex)
                await asyncio.sleep(5)
            await asyncio.sleep(1)

    async def command_ignore(self, d_message):

        async def insert_ignores(selected_items, overwrite=False):
            try:
                connection = mysql.connector.connect(**self.con_.config())
                cursor = connection.cursor(dictionary=True)
                if overwrite:
                    cursor.execute("DELETE FROM `discord_CapRadar_ignore_pilots` WHERE channel_cr = (%s)",
                                   [self.channel.id])
                    cursor.execute("DELETE FROM `discord_CapRadar_ignore_corps` WHERE channel_cr = (%s)",
                                   [self.channel.id])
                    cursor.execute("DELETE FROM `discord_CapRadar_ignore_alliances` WHERE channel_cr = (%s)",
                                   [self.channel.id])
                for id in selected_items['pilots']:
                    cursor.execute(
                        "INSERT IGNORE INTO discord_CapRadar_ignore_pilots(channel_cr,pilot_id) VALUES(%s,%s)",
                        [self.channel.id, id['pilot_id']])
                for id in selected_items['corps']:
                    cursor.execute("INSERT IGNORE INTO discord_CapRadar_ignore_corps(channel_cr,corp_id) VALUES(%s,%s)",
                                   [self.channel.id, id['corp_id']])
                for id in selected_items['alliances']:
                    cursor.execute(
                        "INSERT IGNORE INTO discord_CapRadar_ignore_alliances(channel_cr,alliance_id) VALUES(%s,%s)",
                        [self.channel.id, id['alliance_id']])
                connection.commit()
                await self.channel.send(
                    'Successfully saved the ignore list. You can view currently ignored targets for this channel by running\n\n'
                    '"!csettings !capRadar !viewIgnore"')
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                if connection:
                    connection.rollback()
                raise mysql.connector.DatabaseError
            finally:
                if connection:
                    connection.close()

        async def prompt():
            question = str(
                'This tool will assist in adding ignored entities to your capRadar, most often you will want to ignore friendlies.\n Entities consist of pilots, corporation, or alliances you wish to filter from the radarFeed.\n\n Killmails involving capitals flown by an entity on your ignore list will not be posted if they are the only entities involved in a killmail.\n\n FAQ\n What happens if a killmail has capitals flown by both ignored and non-ignored entities?\n -The killmail will be posted to the channel but the overview of involved capital count will not include friendlies.\n\n What happens if a killmail has capitals only flown by ignored (friendly) entities?\n -The killmail will not be posted to the channel\n\n\n\n Now that you have an idea of how ignore lists work, its time to import entities to ignore.\n\n The easiest way to do this is open your corp/alliance standings menu in EVE, CTRL-A then CTRL-C to select all and copy. Then CTRL-V into this discord channel pressing enter.\n Note: Depending on how many contacts you have you may need to switch pages and copy and paste each page of standings to completely populate your intended ignore list.\n\n If you ever need to import more friendlies just run the command "!csettings !capRadar !ignore" to bring up this tool again. To delete previously imported standings you should select the overwrite option on the confirm import standings dialog.\n\n Please enter or paste the entities you wish to ignore into Discord:')
            response = await self.ask_question(question, d_message, self.client, timeout=200)
            items = str(response.content)
            entities = [i for i in items.split('\n')]
            exact_match = True if len(entities) >= 5 else False
            selected_items = {'pilots': [], 'corps': [], 'alliances': []}
            for i in entities:
                try:
                    entity_select = await self.client.select_entity(d_message, i, exact_match=exact_match)
                    for key, val in entity_select.items():
                        if val is not None:
                            for item in val:
                                selected_items[key].append(item)
                except:
                    pass
            embed = discord.Embed(title='Selected to ignore',
                                  colour=discord.Colour(0x182649),
                                  description='These are the currently selected entities to be added to the capRadar ignore lists.')
            pilots_s = ''
            corps_s = ''
            alliances_s = ''
            for p in selected_items['pilots']:
                pilots_s += str(p['pilot_name'] + '\n')
            for c in selected_items['corps']:
                corps_s += str(c['corp_name'] + '<{}>\n'.format(c['corp_ticker']))
            for a in selected_items['alliances']:
                alliances_s += str(a['alliance_name'] + '<{}>\n'.format(a['ticker']))
            if len(pilots_s) > 1:
                embed.add_field(name="**Pilots**", value=pilots_s, inline=False)
            if len(corps_s) > 1:
                embed.add_field(name="**Corps**", value=corps_s, inline=False)
            if len(alliances_s) > 1:
                embed.add_field(name="**Alliances**", value=alliances_s, inline=False)
            embed.add_field(name="Accept or Decline Changes",
                            value="\n\n**To confirm these changes please enter\n\n0 - Discard Changes\n\n"
                                  "1 - Accept and add to existing ignore list (previously added ignores will still be in effect)\n\n"
                                  "2 - Accept and overwrite/delete existing ignores (previously added ignores will be deleted and replaced)**",
                            inline=False)
            answer = await self.ask_question("{}".format(d_message.author.mention), d_message, self.client, embed=embed,
                                             timeout=90)

            if str(answer.content) == "2" or str(answer.content) == "overwrite":  # todo better matching
                await insert_ignores(selected_items, overwrite=True)
            elif str(answer.content) == "1" or str(answer.content) == "yes":  # todo better matching
                await insert_ignores(selected_items, overwrite=False)
            elif str(answer.content) == "0" or str(answer.content) == "no":
                await self.channel.send("{}\nNo changes have been made".format(d_message.author.mention))
            else:
                await self.channel.send(
                    'Error: You must select either "0" to decline or "1" to accept.\n\nNo changes have been made')

        await prompt()
        self.load_ignores()

    async def listen_command(self, d_message, message):
        sub_command = ' '.join((str(message).split()[1:]))
        if d_message.author == self.client.user:
            return
        if await self.client.lookup_command(sub_command, self.client.commands_all['subc_ignore']):
            await self.command_ignore(d_message)
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_start']):
            await self.command_start()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['subc_stop']):
            await self.command_stop()
        elif await self.client.lookup_command(sub_command, self.client.commands_all['command_allelse']):
            await self.client.command_not_found(d_message)  # todo fix partial commands
        else:
            return

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
        async def prompt():
            db_insert_tracking = {'channel': ch.channel.id}
            system_name = None
            question = str("{}\nThis tool will assist in setting up a capRadar feed.\n\n"
                    "The capRadar alerts you of capital, super, and black ops activity within jump range of a specified system.\n\n"
                    "First, enter the name of your base system you wish to track capitals in range of:\n".format(
                        d_message.author.mention))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            system = await ch.client.select_system(ch.client.m_systems.find(author_answer.content), d_message,
                                                   author_answer.content)
            db_insert_tracking['system_base'] = system['system_id']
            system_name = system['system_name']

            question = str(
                '{}\nPlease specify the maximum capital jump range you wish to track capitals in LYs from your base system. Kills outside of this jump range will not be posted to the channel.\n\n'
                'Example: If you wish to only show capitals active within black ops direct jump range of your base system you would enter "8"\n\n\nMax Radar Range in LYs: '.format(
                    d_message.author.mention))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            try:
                db_insert_tracking['maxLY_fromBase'] = float(author_answer.content)
            except ValueError:
                raise Exception("{} is not a number".format(author_answer.content))

            question = str('{}\nDo you wish to track supers in this capRadar feed?\n\n'
                           'This will track supercarriers, titans, and faction supers/titans\n\nPlease select an option by entering the corresponding number\n\n\n'
                           '0 - No\n'
                           '1 - Yes\n\n'
                           'Your response: '.format(d_message.author.mention))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_supers'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_supers'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            question = str('{}\nDo you wish to track normal capitals in this capRadar feed?\n\n'
                           'This will track carriers, force auxiliary carriers, and dreadnoughts.\n\n'
                           'Note: If you answered yes to tracking supers in the previous prompt and select yes to this prompt you will track both normal capitals in addition to supers.\n\n'
                           'Please select an option by entering the corresponding number\n\n\n'
                           '0 - No\n'
                           '1 - Yes\n\n'
                           'Your response: '.format(d_message.author.mention))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_capitals'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_capitals'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            question = str(
                    '{}\nDo you wish to track black ops battleships in this capRadar feed?\n\n'
                    'This will track black ops battleships\n\nPlease select an option by entering the corresponding number\n\n\n'
                    '0 - No\n'
                    '1 - Yes\n\n'
                    'Your response: '.format(d_message.author.mention))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                db_insert_tracking['track_blops'] = 1
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                db_insert_tracking['track_blops'] = 0
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

            if db_insert_tracking['track_supers'] == 1:
                question = str(
                    '{}\nOn detected supercapital activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                    'Note: if you select disable, supercapital activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                    'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                    'Please select an option by entering the corresponding number\n\n\n'
                    '0 - disable this feature\n'
                    '1 - @ here\n'
                    '2 - @ everyone\n\n'
                    'Your response: '.format(d_message.author.mention))
                author_answer = await capRadar.ask_question(question, d_message, ch.client)
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['super_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['super_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

            if db_insert_tracking['track_capitals'] == 1:
                question = str(
                        '{}\nOn detected capital activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                        'Note: if you select disable, capital activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                        'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                        'Please select an option by entering the corresponding number\n\n\n'
                        '0 - disable this feature\n'
                        '1 - @ here\n'
                        '2 - @ everyone\n\n'
                        'Your response: '.format(d_message.author.mention))
                author_answer = await capRadar.ask_question(question, d_message, ch.client)
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['capital_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['capital_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

            if db_insert_tracking['track_blops'] == 1:
                question = str(
                        '{}\nOn detected blops activity you can have the bot notify the channel by pinging @ here or @ everyone\n\n'
                        'Note: if you select disable, blops activity will still be posted to channel just without pinging @ here or @ everyone.\n\n'
                        'If a killmail involves supercapitals, capitals, and blops the notification setting for the most expensive ship class will be applied.\n\n'
                        'Please select an option by entering the corresponding number\n\n\n'
                        '0 - disable this feature\n'
                        '1 - @ here\n'
                        '2 - @ everyone\n\n'
                        'Your response: '.format(d_message.author.mention))
                author_answer = await capRadar.ask_question(question, d_message, ch.client)
                if str(author_answer.content) == "0" or str(author_answer.content) == "disable":
                    pass
                elif str(author_answer.content) == "1" or str(author_answer.content) == "here":
                    db_insert_tracking['blops_notification'] = '@here'
                elif str(author_answer.content) == "2" or str(author_answer.content) == "everyone":
                    db_insert_tracking['blops_notification'] = '@everyone'
                else:
                    raise Exception('Invalid response, you must enter "0" or "1" or "2"')

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
            question = str(
                '{}\n{}\n\nIf the above values are correct and you wish to initiate radar based on these settings please confirm by accepting\n\n'
                '0 - Decline Addition\n'
                '1 - Accept Addition'.format(d_message.author.mention, st_str))
            author_answer = await capRadar.ask_question(question, d_message, ch.client)
            if str(author_answer.content) == "1" or str(author_answer.content) == "yes":  # todo better matching
                return db_insert_tracking
            elif str(author_answer.content) == "0" or str(author_answer.content) == "no":
                raise Exception("User declined radar settings")
            else:
                raise Exception('Invalid response, you must enter "0" for no or "1" for yes')

        return (await prompt())
