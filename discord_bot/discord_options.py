from . import discord_main
import discord
import asyncio


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
        raise None


class mapper_index(object):
    def __init__(self,discord_client_object,message_object,timeout_seconds=30):
        assert isinstance(message_object,discord.Message)
        assert isinstance(discord_client_object,discord_main.Discord_Insight_Client)
        self.message = message_object
        self.__option_container = []
        self.__printout_format = []
        self.__mention = "{}".format(self.message.author.mention)
        self.__header_text = ""
        self.__footer_text = "Select an option by entering it's number:"
        self.__timeout_seconds = int(timeout_seconds)
        self.discord_client = discord_client_object

    def set_main_header(self,main_header_txt:str):
        self.__header_text = main_header_txt

    def set_footer_text(self,main_footer_text:str):
        self.__footer_text = main_footer_text

    def add_blank_line(self):
        self.__printout_format.append("")

    def add_header_row(self,header_txt):
        self.__printout_format.append("-----{}-----\n".format(str(header_txt)))

    def __current_option_index(self)->int:
        return int(len(self.__option_container))

    def add_option(self, mapper_option_obj:option_calls_coroutine):
        if isinstance(mapper_option_obj, option_calls_coroutine) or isinstance(mapper_option_obj,option_returns_object):
            mapper_option_obj.set_index(self.__current_option_index())
            self.__option_container.append(mapper_option_obj)
            self.__printout_format.append("{}".format(str(mapper_option_obj)))
        else:
            raise AssertionError

    def __str__(self):
        __str_item = self.__mention + "\n" + self.__header_text + "\n\n\n"
        for i in self.__printout_format:
            __str_item += (str(i) + "\n\n")
        __str_item += "\n\n" + self.__footer_text
        return __str_item + "\n"

    async def check_conditions(self):
        try:
            assert self.__current_option_index() > 0
        except AssertionError:
            await self.message.channel.send("One of the assertions for the option container failed. This is likely a programming error")
            raise None

    def isInt(self,value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    async def check_response(self,response):
        try:
            assert self.isInt(response)
            assert int(response) >= 0 and int(response) < self.__current_option_index()
        except AssertionError:
            await self.message.channel.send("You must enter a number between 0 and {} but you entered {}".format(str(self.__current_option_index() - 1), str(response)))
            raise None

    async def add_additional(self):
        pass

    def get_option(self,index:int)->option_calls_coroutine:
        return self.__option_container[index]

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
            await self.message.channel.send(str(self))
            __response = await self.discord_client.wait_for('message', check=is_author, timeout=self.__timeout_seconds)
            return await self.response_action(__response.content)
        except asyncio.TimeoutError:
            await self.message.channel.send("{}\nSorry, but you took to long to respond. You must respond within {} seconds.".format(self.message.author.mention, str(self.__timeout_seconds)))
            raise None


class mapper_index_withAdditional(mapper_index):
    async def add_additional(self):
        self.add_header_row("Additional options")
        self.add_option(option_cancel())

class mapper_return_yes_no(mapper_index):
    def __init__(self, discord_client_object, message_object, timeout_seconds=30):
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


class mapper_return_noOptions_requiresInt(mapper_return_noOptions):
    async def check_response(self,response):
        if not self.isInt(response):
            await self.message.channel.send("You entered an invalid number. You must enter a number but you entered "
                                            "'{}'".format(str(response)))
            raise None

    async def response_action(self, response):
        await self.check_response(response)
        return response



