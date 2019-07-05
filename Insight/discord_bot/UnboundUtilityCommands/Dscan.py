from .UnboundCommandBase import *
from InsightSubsystems.TheWatcher import TheWatcher


class Dscan(UnboundCommandBase):
    def __init__(self, unbound_service):
        super().__init__(unbound_service)
        self.watcher: TheWatcher.TheWatcher = TheWatcher.TheWatcher.get_instantiated()

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) -> str:
        raise InsightExc.DiscordError.DiscordPermissions("Insight must have the embed links channel role in order "
                                                         "to post Discord rich embed objects containing the dscan"
                                                         "result. Regular text output is not supported by the "
                                                         "Insight dscan service. ")

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        e = discord.Embed()
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name="Dscan (Beta)")
        e.set_footer(text='Pilot Dscan')
        e.description = ""
        pilot_objects = []
        for s in message_text.split('\n'):
            pilot = self.watcher.get_pilot(s.strip())
            if pilot:
                pilot_objects.append(pilot)
        pilot_block = ""
        for p in pilot_objects:
            pilot_block += (p.embed_row_str() + '\n')
        e.add_field(name='Characters', value="```{}```".format(pilot_block), inline=False)
        return e

