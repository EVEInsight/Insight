from . import discord_main
import discord
import asyncio
import InsightExc
import datetime
from InsightUtilities import LimitManager


class option_calls_coroutine(object):
    def __init__(self,name="",description="",coroutine_object=None):
        self.index = 0
        self.name = name
        self.description = description
        self.mapper_object = coroutine_object

    def set_index(self,new_index:int):
        self.index = new_index

    async def __call__(self, *args, **kwargs):
        await self.mapper_object

    def __str__(self):
        return "{}--{}  {}".format(str(self.index),str(self.name),str(self.description))


class option_returns_object(option_calls_coroutine):
    def __init__(self,name="",description="",return_object=None):
        super(option_returns_object, self).__init__(name, description, return_object)

    async def __call__(self, *args, **kwargs):
        return self.mapper_object


class option_cancel(option_calls_coroutine):
    def __init__(self,name="Cancel",description="",return_object=None):
        super(option_cancel, self).__init__(name,description,return_object)

    async def __call__(self, *args, **kwargs):
        raise InsightExc.User.Cancel


class mapper_index(object):
    def __init__(self, discord_client_object, message_object, timeout_seconds=120):
        assert isinstance(message_object,discord.Message)
        assert isinstance(discord_client_object,discord_main.Discord_Insight_Client)
        self.message = message_object
        self._option_container = []
        self._printout_format = []
        try:  # remove mention if author is not filled
            self._mention = "{}".format(self.message.author.mention)
        except AttributeError:
            self._mention = ""
        self._header_text = ""
        self._footer_text = "Select an option by entering its number:"
        self._timeout_seconds = int(timeout_seconds)
        self.discord_client = discord_client_object
        self.e_header_container = ['Options']
        self.e_body_container = []
        self.header_index = 0
        self.maxbitlength = 16

    def set_main_header(self,main_header_txt:str):
        self._header_text = main_header_txt

    def set_footer_text(self,main_footer_text:str):
        self._footer_text = main_footer_text

    def add_blank_line(self):
        self._printout_format.append("")

    def add_header_row(self, header_txt):
        self._printout_format.append("\n-----{}-----".format(str(header_txt)))
        if self.header_index == 0 and len(self.e_body_container) == 0:
            self.e_header_container = [str(header_txt)]
        else:
            self.e_header_container.append(str(header_txt))
            self.header_index += 1

    def _current_option_index(self)->int:
        return int(len(self._option_container))

    def set_bit_length(self, bit_l: int):
        self.maxbitlength = bit_l

    def add_option(self, mapper_option_obj: option_calls_coroutine):
        if self._current_option_index() > 400:
            raise InsightExc.userInput.TooManyOptions
        if isinstance(mapper_option_obj, option_calls_coroutine) or isinstance(mapper_option_obj,option_returns_object):
            mapper_option_obj.set_index(self._current_option_index())
            self._option_container.append(mapper_option_obj)
            self._printout_format.append("{}".format(str(mapper_option_obj)))
            try:
                self.e_body_container[self.header_index].append(str(mapper_option_obj))
            except IndexError:
                self.e_body_container.append([str(mapper_option_obj)])
        else:
            raise AssertionError

    def get_embed(self):
        try:
            embed = discord.Embed()
            embed.title = ""
            embed.color = discord.Color(659493)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_author(name=self.name())
            embed.set_footer(text='Timeout: {}s'.format(self._timeout_seconds))
            embed.description = self._header_text
            for index, h in enumerate(self.e_header_container):
                try:
                    results = self.e_body_container[index]
                except IndexError:
                    break
                results.reverse()
                options_str = ""
                total_len = 0
                pg_count = 0
                while len(results) != 0:
                    if pg_count >= 20:
                        raise InsightExc.User.TooManyOptions
                    add_str = "{}\n\n".format(str(results.pop()))
                    if total_len + len(add_str) > 950:
                        options_str = '```{}```'.format(options_str) if options_str else '```empty```'
                        t_h = '{}'.format(h) if pg_count == 0 else '{} - continued ({})'.format(h, pg_count)
                        embed.add_field(name=t_h, value=options_str, inline=False)
                        options_str = ""
                        pg_count += 1
                        total_len = 0
                    options_str += add_str
                    total_len += len(add_str)
                if options_str:
                    options_str = '```{}```'.format(options_str) if options_str else '```empty```'
                    t_h = '{}'.format(h) if pg_count == 0 else '{} - continued ({})'.format(h, pg_count)
                    embed.add_field(name=t_h, value=options_str, inline=False)
            embed.add_field(name='Info', value=self._footer_text)
            return embed
        except Exception as ex:
            if not isinstance(ex, InsightExc.InsightException):
                print(ex)
            raise InsightExc.DiscordError.EmbedOptionsError

    def __str__(self):
        __str_item = self._mention + "\n" + self._header_text + "\n\n"
        for i in self._printout_format:
            __str_item += (str(i) + "\n\n")
        __str_item += "\n\n" + self._footer_text
        if len(__str_item) >= 1950:
            raise InsightExc.User.TooManyOptions
        return __str_item + "\n"

    async def check_conditions(self):
        try:
            assert self._current_option_index() > 0
        except AssertionError:
            raise InsightExc.User.InsightProgrammingError

    def isInt(self,value):
        try:
            if len(value) > self.maxbitlength:
                raise InsightExc.User.BitLengthExceeded
            int(value)
            return True
        except ValueError:
            return False

    async def check_response(self,response):
        try:
            assert self.isInt(response)
            assert int(response) >= 0 and int(response) < self._current_option_index()
        except AssertionError:
            raise InsightExc.User.InvalidIndex("You must enter a number between 0 and {}, but you entered '{}'."
                                               "".format(str(self._current_option_index() - 1), str(response)))

    async def add_additional(self):
        pass

    def get_option(self,index:int)->option_calls_coroutine:
        return self._option_container[index]

    async def response_action(self, response):
        await self.check_response(response)
        cor = self.get_option(int(response))
        return await cor()

    async def __call__(self):
        def is_author(m: discord.Message):
            return m.author == self.message.author and m.channel == self.message.channel
        try:
            await self.add_additional()
            await self.check_conditions()
            if isinstance(self.message.channel, discord.TextChannel):
                p: discord.Permissions = self.message.channel.permissions_for(self.message.channel.guild.me)
                if p.embed_links:
                    try:
                        async with (await LimitManager.cm_hp(self.message)):
                            await self.message.channel.send(embed=self.get_embed())
                    except InsightExc.DiscordError.EmbedOptionsError:
                        async with (await LimitManager.cm_hp(self.message)):
                            await self.message.channel.send(str(self))
                else:
                    async with (await LimitManager.cm_hp(self.message)):
                        await self.message.channel.send(str(self))
            else:
                async with (await LimitManager.cm_hp(self.message)):
                    await self.message.channel.send(embed=self.get_embed())
            __response = await self.discord_client.wait_for('message', check=is_author, timeout=self._timeout_seconds)
            return await self.response_action(__response.content)
        except asyncio.TimeoutError:
            raise InsightExc.User.InputTimeout("Sorry, but you took too long to respond. You must respond within {} "
                                               "seconds.".format(str(self._timeout_seconds)))
        except discord.HTTPException as ex:
            if ex.code == 50035 and ex.status == 400:
                raise InsightExc.User.TooManyOptions
            else:
                raise ex

    def name(self):
        return "Option Selection"


class mapper_index_withAdditional(mapper_index):
    async def add_additional(self):
        self.add_header_row("Additional Options")
        self.add_option(option_cancel())


class mapper_return_yes_no(mapper_index):
    def __init__(self, discord_client_object, message_object, timeout_seconds=120):
        super(mapper_return_yes_no, self).__init__( discord_client_object, message_object, timeout_seconds)
        self.set_footer_text("Enter either '1' for yes or '0' for no:")
        self.add_option(option_returns_object("No",return_object=False))
        self.add_option(option_returns_object("Yes",return_object=True))


class mapper_return_noOptions(mapper_index):
    async def add_option(self, mapper_option_obj:option_calls_coroutine):
        raise NotImplementedError

    async def check_conditions(self):
        pass

    async def response_action(self, response):
        return response

    def name(self):
        return "Input/Search"


class mapper_return_noOptions_requiresInt(mapper_return_noOptions):
    def __init__(self, discord_client_object, message_object, timeout_seconds=120):
        super().__init__(discord_client_object, message_object, timeout_seconds)
        self.set_footer_text("Enter an integer number: Ex: 5, 10, 0, etc.")

    async def check_response(self,response):
        if not self.isInt(response):
            raise InsightExc.User.NotInteger(
                ("You entered an invalid number. You must enter an integer, but you entered"
                                              " '{}' which is not an integer.".format(str(response))))

    async def response_action(self, response):
        await self.check_response(response)
        return str(abs(int(response)))

    def name(self):
        return "Integer Input"


class mapper_return_noOptions_requiresFloat(mapper_return_noOptions):
    def __init__(self, discord_client_object, message_object, timeout_seconds=120):
        super().__init__(discord_client_object, message_object, timeout_seconds)
        self.set_footer_text("Enter a number: Ex: 5.2, 1.3, 5, 0, etc.")

    def isFloat(self, value):
        try:
            if len(value) > self.maxbitlength:
                raise InsightExc.User.BitLengthExceeded
            float(value)
            return True
        except ValueError:
            return False

    async def check_response(self,response):
        if not self.isFloat(response):
            raise InsightExc.User.NotFloat("You entered an invalid number. You must enter a float, but you entered"
                                           " '{}' which is not a float.".format(str(response)))

    async def response_action(self, response):
        await self.check_response(response)
        return str(abs(float(response)))

    def name(self):
        return "Decimal Input"



