import asyncio
import datetime
import difflib
import itertools
import math
import random
from operator import itemgetter

import discord

from access.EntityUpdates import EntityUpdates
from access.cap_info import cap_info
from access.systems.systems import fa_systems
from access.zk import zk_thread
from bot.channel_manager.channel_manager import channel_manager
from database.database_connection import db_con


class D_client(discord.Client):
    def __init__(self, cf_file, args):
        super().__init__()
        self.config_file = cf_file
        self.arguments = args
        self.db_c = db_con(cf_file=cf_file, args=args)
        self.m_systems = fa_systems(con=self.db_c, cf_file=cf_file, args=args)
        self.cap_info = cap_info(cf_info=cf_file, args=args)
        self.zk = zk_thread(con=self.db_c, cf_info=cf_file, args=args)
        self.en_updates = EntityUpdates(con=self.db_c, cf_info=cf_file, args=args)

        self.channel_manager = channel_manager(con=self.db_c, cf_info=cf_file, args=args, discord_client=self)

        self.dotlan_url_range = "http://evemaps.dotlan.net/range/{},5/{}"
        self.dotlan_url_jplanner = "http://evemaps.dotlan.net/jump/{},555/{}:{}"

        self.import_vars()
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def select_system(self, system_dict, message, original_lookup):
        if len(system_dict) == 0:
            await message.channel.send("{}\nI could not find the system \"{}\"\nPlease try a different system".format(
                message.author.mention, original_lookup))
            raise KeyError("unable to find system")
        elif len(system_dict) == 1:
            return system_dict[0]
        else:
            systems = str("")
            count = 0
            for i in system_dict:
                count += 1
                systems += (str("{}. {} ({})\n").format(count, i["system_name"], i["region_name"]))
            with message.channel.typing():
                await message.channel.send(
                    "{}\nMultiple systems found matching \"{}\" \n\nPlease select one by entering it's number\nex type \"1\" to select the first result:\n\n{}".format(
                                              message.author.mention, original_lookup, systems))
            def select_system_check(m):
                return m.author == message.author
            try:
                resp = await self.wait_for('message', timeout=10, check=select_system_check)
            except asyncio.TimeoutError:
                await message.channel.send("{}\nSorry, but you took to long to respond".format(message.author.mention))
                raise TimeoutError("response timeout")
            else:
                if int(resp.content) > count or int(resp.content) <= 0:
                    await message.channel.send("{}\n\"{}\" index is out of range, please select a number between 1 and {}".format(message.author.mention,str(resp.content), str(count)))
                    raise KeyError("wrong index select")
                else:
                    return(system_dict[int(resp.content)-1])

    async def select_entity(self, entity_dict, message, original_lookup):
        # if len(entity_dict) == 0:
        #     await message.channel.send("{}\nI could not find the alliance \"{}\"\nPlease try a different alliance".format(
        #         message.author.mention, original_lookup))
        #     raise KeyError("unable to find alliance")
        # elif len(entity_dict) == 1:
        #     return entity_dict[0]
        # else:
        #     systems = str("")
        #     count = 0
        #     for i in entity_dict:
        #         count += 1
        #         systems += (str("{}. {} ({})\n").format(count, i["system_name"], i["region_name"]))
        #     with message.channel.typing():
        #         await message.channel.send(
        #             "{}\nMultiple alliances found matching \"{}\" \n\nPlease select one by entering it's number\nex type \"1\" to select the first result:\n\n{}".format(
        #                                       message.author.mention, original_lookup, systems))
        #     def select_system_check(m):
        #         return m.author == message.author
        #     try:
        #         resp = await self.wait_for('message', timeout=10, check=select_system_check)
        #     except asyncio.TimeoutError:
        #         await message.channel.send("{}\nSorry, but you took to long to respond".format(message.author.mention))
        #         raise TimeoutError("response timeout")
        #     else:
        #         if int(resp.content) > count or int(resp.content) <= 0:
        #             await message.channel.send("{}\n\"{}\" index is out of range, please select a number between 1 and {}".format(message.author.mention,str(resp.content), str(count)))
        #             raise KeyError("wrong index select")
        #         else:
        #             return(entity_dict[int(resp.content)-1])
        print(entity_dict)

    async def lookup_ship(self,message, original_lookup):
        for key, val in self.cap_info.search_cap_type.items():
            if any([s.lower().startswith(original_lookup.lower()) for s in val]):
                return (key)
        await message.channel.send("{}\nI could not find the shiptype \"{}\"\nPlease try again".format(
                message.author.mention, original_lookup))
        raise KeyError("ship not found")

    async def command_range(self, message):
        items = (str(message.content).split()[1:])
        if len(items) == 0:
            await message.channel.send("{}\n!range\nUsage:\n"
                                       "Generates links to dotlan with the selected system and shiptypes. JDC 5 is assumed.\n"
                                       "Note: partial system names and ship clases are supported. If multiple systems match your query you will be able to select one.\n\n"
                                       "Example Usage:\n\n"
                                       "\"!range system_1 ship_class\" \n--returns a Dotlan range map for the specified system_1 and ship_class\n"
                                       "ex. \"!range jit ava\"\n\n"
                                       "\"!range system_1 system_2\" \n--prints ship classes and JDC level needed to reach system_2 from system_1\n"
                                       "ex. \"!range Jita Obe\"\n\n"
                                       "\"!range system_1 system_2 ship_class\" \n--returns a Dotlan jump route map between system_1 and system_2 for ship_class\n"
                                       "ex. \"!range Jita HED-GP Anshar\"".format(message.author.mention))
        elif len(items) == 2:
            system_1 = await self.select_system(self.m_systems.find(items[0]), message, items[0])
            ship_class_1 = await self.lookup_ship(message, items[1])
            await message.channel.send("{}\n{}".format(
                                          message.author.mention, self.dotlan_url_range.format(ship_class_1,system_1["system_name"])))
        elif len(items) == 3:
            system_1 = await self.select_system(self.m_systems.find(items[0]), message, items[0])
            system_2 = await self.select_system(self.m_systems.find(items[1]), message, items[1])
            ship_class_1 = await self.lookup_ship(message, items[2])
            await message.channel.send("{}\n{}".format(
                                          message.author.mention, self.dotlan_url_jplanner.format(ship_class_1, system_1["system_name"], system_2["system_name"])))

    async def command_hit(self, message):
        items = (str(message.content).split()[1:])
        if len(items) <= 1:
            await message.channel.send("{}\n!inrange\nUsage:\n"
                                       "Determines ship classes capable of reaching system_2 from system_1\n"
                                       "Note: partial system names are supported. If multiple systems match your query you will be able to select one.\n\n"
                                       "Example Usage:\n\n"
                                       "\"!inrange system_1 system_2\" \n\n"
                                       .format(message.author.mention))
        else:
            system_1 = await self.select_system(self.m_systems.find(items[0]),message,items[0])
            system_2 = await self.select_system(self.m_systems.find(items[1]), message, items[1])
            ly_range = self.m_systems.ly_range(system_1, system_2)
            in_range= {}
            out_range= {}
            for key, val in self.cap_info.range.items():
                if float(val["JDC5"]) > ly_range:
                    in_range[str(key)] = ["JDC5"]
                    if float(val["JDC4"]) > ly_range:
                        in_range[key].insert(0, "JDC4")
                    else:
                        out_range[str(key) + " JDC4"] = str(
                            "{} mid".format(int(math.floor(ly_range / float((val["JDC4"]))))))
                else:
                    out_range[str(key) + " JDC5"] = str(
                        "{} mid".format(int(math.floor(ly_range / float((val["JDC5"]))))))
                    out_range[str(key) + " JDC4"] = str(
                        "{} mid".format(int(math.floor(ly_range / float((val["JDC4"]))))))
            resp_message = "{}\n{}->{} ({} lys)\n".format(message.author.mention, system_1["system_name"],
                                                          system_2["system_name"], str(round(ly_range, 3)))
            resp_message += ("====in range====\n")
            for key, val in in_range.items():
                line = str(key + ": ")
                for i in val:
                    line += str(i + " ")
                resp_message += (line + "\n")
            resp_message += ("\n====out of range====\n")
            for key, val in out_range.items():
                line = str(key + ": ")
                line += str(val)
                resp_message += (line + "\n")
            await message.channel.send(resp_message)

    async def command_npc(self, message):
        items = (str(message.content).split()[1:])
        if len(items) == 0:
            pass
            # command usage
        else:
            for i in items:
                system_1 = await self.select_system(self.m_systems.find(i), message, i)
                kills_last = self.m_systems.pve_stats.npc_kills_last_hour(system_1)
                kills_delta = self.m_systems.pve_stats.npc_delta(system_1)
                next_update = round(
                    ((self.m_systems.pve_stats.expires - datetime.datetime.utcnow()).total_seconds() / 60), 1)
                last_update = round(
                    ((datetime.datetime.utcnow() - self.m_systems.pve_stats.last_updated).total_seconds() / 60), 1)

                npc = str("{:<11} {:<5} ({:+})\n".format("NPC Kills:", kills_last['npc_kills'],
                                                         kills_delta['npc_kills']))
                ship = str("{:<12} {:<5} ({:+})\n".format("Ship Kills:", kills_last['ship_kills'],
                                                          kills_delta['ship_kills']))
                pod = str("{:<12} {:<5} ({:+})\n".format("Pod Kills:", kills_last['pod_kills'],
                                                         kills_delta['pod_kills']))
                print(str(npc + ship + pod))
                await message.channel.send("{}\nSystem: {} ({})\n\n"
                                           "{}\n"
                                           "Delta: {}   ->   {}\n"
                                           "Last Update: {} minutes ago\n"
                                           "Next Update: {} minutes\n".format(
                    message.author.mention, system_1['system_name'], system_1['region_name'],
                    str(npc + ship + pod),
                    kills_delta['time1'], kills_delta['time0'],
                    last_update,
                    next_update))

    async def command_radar(self, message):
        # todo change name of function
        items = (str(message.content).split()[1:])
        if len(items) == 0:
            pass
            # todo usage
        elif len(items) == 2:
            systems_list = []
            system_1 = await self.select_system(self.m_systems.find(items[0]), message, items[0])
            ship_type = await self.lookup_ship(message, items[1])
            jump_range = self.cap_info.return_jump_range(ship=ship_type)
            next_update = round(
                ((self.m_systems.pve_stats.expires - datetime.datetime.utcnow()).total_seconds() / 60), 1)
            last_update = round(
                ((datetime.datetime.utcnow() - self.m_systems.pve_stats.last_updated).total_seconds() / 60), 1)
            tmp_test = self.m_systems.systems_in_range(system_1, jump_range)
            for i in tmp_test:
                systems_list.append({'system_name': i['system_name'],
                                     'npc': self.m_systems.pve_stats.npc_kills_last_hour(i)['npc_kills'],
                                     'delta': self.m_systems.pve_stats.npc_delta(i)['npc_kills']})
            systems_list.sort(key=lambda k: k['npc'], reverse=True)

            header = str(
                "{}\nSystems by Highest NPC Kills and delta in range of {}({})({} lys)".format(message.author.mention,
                                                                                               system_1['system_name'],
                                                                                               system_1['region_name'],
                                                                                               jump_range))
            header_2 = str("\n{} systems as of: {} minutes ago\nNext update in: {} minutes\n"
                           "======systems==========\n".format(len(systems_list),
                                                              last_update,
                                                              next_update))
            body = str("")
            for i in systems_list:
                body += str(i['system_name'] + " {} ({:+})\n".format(i['npc'], i['delta']))

            text = (header + header_2 + body)
            n = 1999
            for i in ([text[i:i + n] for i in range(0, len(text), n)]):  # todo add custom length
                await message.channel.send(i)
        else:
            pass  # todo else

    async def command_help(self, message):
        await message.channel.send('{}\n'
                                   'This bot watches for commands starting with "!"\n\n'
                                   'Available commands:\n\n'
                                   '"!range" \tprovides Dotlan range and jump route maps\n\n'
                                   'Usage:\n'
                                   '"!range system_a ship_type"\n'
                                   '"!range system_a system_b ship_type"\n\n\n'
                                   '"!hit" \tlists ships within jump range of a system, if out of range prints the required # mids\n\n'
                                   'Usage:\n'
                                   '"!hit system_a system_b"\n\n\n'
                                   '"!npc" \tLists npc, ship, pod kills and delta for the system.\nNote: Multiple systems can be looked up at once, just seperate system names by spaces.\n\n'
                                   'Usage:\n'
                                   '"!npc system_a ...."\n\n\n'
                                   .format(message.author.mention)
                                   )

    async def command_about(self, message):
        await message.channel.send(
            'eve-insight an EVE Online Discord Helper Bot\nhttps://github.com/Nathan-LS/EVE-Insight')

    async def command_not_found(self, message):
        similar_commands = await self.most_similar_word(str(message.content), self.any_command)
        other_commands_str = "Did you mean?\n"
        if len(similar_commands) == 0:
            other_commands_str = ""
        else:
            for i in similar_commands:
                other_commands_str += str('"' + i + '" \n')
        await message.channel.send('{}\nThe command: "{}" was not found.\n{}\n'
                                   'Type "!commands" or "!help" to see a list of commands or for more help with this application\n'
                                   ''.format(message.author.mention, message.content, other_commands_str))

    async def command_mball(self, message):
        await message.channel.send("{}\n{}".format(message.author.mention, random.choice(self.mball_responses)))

    async def command_ships(self, message):
        def sortAndGroup(raw_data, id=None, name=None, ticker=None):
            return_list = []
            group_key = itemgetter(id, name, ticker)
            sorted_group = {k: list(v) for k, v in itertools.groupby(sorted(raw_data, key=group_key), key=group_key)}
            for key, val in sorted_group.items():
                temp_dict = {str(id): key[0], str(name): key[1], str(ticker): key[2], 'total_pilots': len(val),
                             'ships': []}
                unknown_ships = {'name': 'unknown', 'alive_total': len(val), 'dead_total': 0, 'total': 0}

                pilotsFlyingRecentShip = [pilot for pilot in val if
                                          pilot.get('killmail_time') > datetime.datetime.utcnow() - datetime.timedelta(
                                              minutes=90) or pilot.get('is_super') == 1]
                unknown_ships['alive_total'] -= len(pilotsFlyingRecentShip)

                temp_ships_used = {k: list(v) for k, v in
                                   itertools.groupby(sorted(pilotsFlyingRecentShip, key=itemgetter('ship_name')),
                                                     key=itemgetter('ship_name'))}
                for ship_name, pilots_flying in temp_ships_used.items():
                    ship_to_append = dict(name=ship_name,
                                          dead_total=sum((1 for k in pilots_flying if k.get('is_victim') == 1)))
                    ship_to_append['alive_total'] = len(pilots_flying) - ship_to_append['dead_total']
                    ship_to_append['total'] = ship_to_append['dead_total'] + ship_to_append['alive_total']
                    temp_dict['ships'].append(ship_to_append)
                temp_dict['ships'] = sorted(temp_dict['ships'], key=itemgetter('alive_total'), reverse=True)

                unknown_ships['total'] = unknown_ships['dead_total'] + unknown_ships['alive_total']
                if unknown_ships['total'] != 0:
                    temp_dict['ships'].append(unknown_ships)
                return_list.append(temp_dict)
            return_list = sorted(return_list, key=itemgetter('total_pilots'), reverse=True)
            return (return_list)

        try:
            items = (str(message.content).split(None, 1)[1])
        except IndexError:
            await message.channel.send(
                '{}\nYou must provide a copy paste of local to view ship types.\nUsage: "!ships CTRL-V"'.format(
                    message.author.mention))
            return
        by_alliance = []
        by_corp = []
        by_pilot = []
        char_not_found = []
        for i in items.split('\n'):
            resp = self.zk.pilot_name_to_ships(i)
            if resp is None:
                char_not_found.append(i)
            elif resp['alliance_id'] is not None:
                by_alliance.append(resp)
            else:
                by_corp.append(resp)
        total_count = int(len(by_alliance) + len(by_corp) + len(by_pilot) + len(char_not_found))

        embed = discord.Embed(title="Local Scan of {} pilots".format(total_count), colour=discord.Colour(0x182649),
                              description="Showing pilots grouped by alliance/corp and ship count based on"
                                          " activity in the last 90 minutes\nCould not find details for {} pilots. "
                                          "This means they were not on a recorded "
                                          "killmail recently".format(len(char_not_found)))
        embed.set_author(name="Page (1/1)", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
        # embed.set_footer(text="footer", icon_url="https://cdn.discordapp.com/embed/avatars/0.png") #todo change footer
        embed.add_field(name="**(corp/alliance name)<tkr> count**",
                        value="```css\n{:<12} {:<12}{:>3}({:})\n\n.```".format(' ', 'ship', 'alive',
                                                                               'dead'))  # todo clean header
        for i in sortAndGroup(by_alliance, id='alliance_id', name='alliance_name', ticker='alliance_ticker'):
            field_name = "**{al_name}<{al_ticker}> {al_t}**".format(al_name=i['alliance_name'],
                                                                    al_ticker=i['alliance_ticker'],
                                                                    al_t=str(i['total_pilots']))
            field_value = ""
            for ship_types in i['ships']:
                raw_str = str("{space:<12} {ship:<12}{alive_t:>3} ({dead_t:-})".format(space=' ',
                                                                                       ship=ship_types['name'],
                                                                                       alive_t=str(
                                                                                           ship_types['alive_total']),
                                                                                       dead_t=-1 * int(ship_types[
                                                                                                           'dead_total'])))  # todo fix negative ship loss
                format_css = "```css\n{}```"
                format_http = "```HTTP\n{}```"
                if ship_types['name'] == "unknown":
                    field_value += str(format_http.format(raw_str))
                else:
                    field_value += str(format_css.format(raw_str))
            embed.add_field(name=field_name, value=field_value, inline=False)
        for i in sortAndGroup(by_corp, id='corporation_id', name='corp_name', ticker='corp_ticker'):
            field_name = "**{al_name}<{al_ticker}> {al_t}**".format(al_name=i['corp_name'],
                                                                    al_ticker=i['corp_ticker'],
                                                                    al_t=str(i['total_pilots']))
            field_value = ""
            for ship_types in i['ships']:
                raw_str = str("{space:<12} {ship:<12}{alive_t:>3} ({dead_t:-})".format(space=' ',
                                                                                       ship=ship_types['name'],
                                                                                       alive_t=str(
                                                                                           ship_types['alive_total']),
                                                                                       dead_t=-1 * int(ship_types[
                                                                                                           'dead_total'])))  # todo fix negative ship loss
                format_css = "```css\n{}```"
                format_http = "```HTTP\n{}```"
                if ship_types['name'] == "unknown":
                    field_value += str(format_http.format(raw_str))
                else:
                    field_value += str(format_css.format(raw_str))
            embed.add_field(name=field_name, value=field_value, inline=False)

        await message.channel.send("{}".format(message.author.mention), embed=embed)

    async def most_similar_word(self, word, lookup_list):
        return difflib.get_close_matches(word, lookup_list)
    async def lookup_command(self, message, command_list):
        return any((message.lower()).startswith(i.lower()) for i in command_list)

    def populate_commands(self):
        self.commands_all = {}
        self.any_command = []
        for key, val in self.config_file.items('discord_bot_commands'):
            self.commands_all[key] = [i for i in val.split('\n')]
        for item in self.commands_all.values():
            for i in item:
                self.any_command.append(i)

    def import_vars(self):
        self.populate_commands()
        self.mball_responses = [i for i in self.config_file["discord_bot"]['responses_mball'].split('\n')]

    async def on_message(self, message):
        if message.author == self.user:
            return
        if await self.lookup_command(message.content, self.commands_all['command_range']):
            await self.command_range(message)
        elif await self.lookup_command(message.content, self.commands_all['command_hit']):
            await self.command_hit(message)
        elif await self.lookup_command(message.content, self.commands_all['command_npc']):
            await self.command_npc(message)
        elif await self.lookup_command(message.content, self.commands_all['command_radar']):
            await self.command_radar(message)
        elif await self.lookup_command(message.content, self.commands_all['command_help']):
            await self.command_help(message)
        elif await self.lookup_command(message.content, self.commands_all['command_about']):
            await self.command_about(message)
        elif await self.lookup_command(message.content, self.commands_all['command_mball']):
            await self.command_mball(message)
        elif await self.lookup_command(message.content, self.commands_all['command_ships']):
            await self.command_ships(message)
        elif await self.lookup_command(message.content, self.commands_all['command_channel_settings']):
            await self.channel_manager.command_to_channel(message)
        elif await self.lookup_command(message.content, self.commands_all['command_allelse']):
            await self.command_not_found(message)
        else:
            return

    @staticmethod
    def bot_run(cf_file, args):
        config_file = cf_file
        client = D_client(config_file, args)
        client.run(config_file["discord"]["token"], cf_file=config_file)
