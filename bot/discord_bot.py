import asyncio

import discord

from database.database_access import *


class D_client(discord.Client):
    def __init__(self, config_file):
        super().__init__()
        self.config = config_file
        self.db_c = db_con("config.ini")
        self.m_systems = fa_systems(self.db_c)
        self.cap_info = cap_info()
        #self.channel_man = channel_manager()

        self.dotlan_url_range = "http://evemaps.dotlan.net/range/{},5/{}"
        self.dotlan_url_jplanner = "http://evemaps.dotlan.net/jump/{},555/{}:{}"
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    # async def send_message(self,message,channel_id):
    #     await self.wait_until_ready()
    #     print("p send message")


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
                await message.channel.send("{}\nMultiple systems found matching \"{}\" \nPlease select one by entering it's number\nex type \"1\" to select the first result:\n\n{}".format(
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
    async def lookup_ship(self,message, original_lookup):
        for key, val in self.cap_info.search_cap_type.items():
            if any([s.lower().startswith(original_lookup.lower()) for s in val]):
                return (key)
        await message.channel.send("{}\nI could not find the shiptype \"{}\"\nPlease try again".format(
                message.author.mention, original_lookup))
        raise KeyError("ship not found")
    async def command_range(self, message):
        command_rem = (str(message.content).replace("!range", ''))
        items = []
        for i in command_rem.split():
            items.append(i)
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
    async def command_hit(self,message):
        command_rem = (str(message.content).replace("!hit", ''))
        items = []
        for i in command_rem.split():
            items.append(i)
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

    async def command_npc(self,message):
        command_rem = (str(message.content).replace("!npc", ''))
        items = []
        for i in command_rem.split():
            items.append(i)
        if len(items) <= 1:
            pass
            # command usage
        elif len(items) == 1:
            pass
        else:
            system_1 = await self.select_system(self.m_systems.find(items[0]), message, items[0])
            tmp_test = self.m_systems.systems_in_range(system_1, 8)
            for i in tmp_test:
                print(i)

    async def command_about(self, message):
        await message.channel.send(
            'eve-insight an EVE Online Discord Helper Bot\nhttps://github.com/Nathan-LS/EVE-Insight')
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('!range'):
            await self.command_range(message)
        elif message.content.startswith('!hit'):
            await self.command_hit(message)
        elif message.content.startswith('!npc'):
            await self.command_npc(message)
        elif message.content.startswith('!about'):
            await self.command_about(message)
    @staticmethod
    def bot_run():
        config_file = configparser.ConfigParser()
        config_file.read("config.ini")
        client = D_client(config_file)
        client.run(config_file["discord"]["token"])