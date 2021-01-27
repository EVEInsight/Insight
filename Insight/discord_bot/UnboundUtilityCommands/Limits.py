from .UnboundCommandBase import *
from InsightUtilities import LimitManager
from functools import partial


class Limits(UnboundCommandBase):
    @classmethod
    def mention(cls):
        return False

    async def get_limiters(self, message, no_redact=False):
        l = await LimitManager.cm(message)
        return await self.loop.run_in_executor(None, partial(l.get_self_and_parent_stats, no_redact))

    def header(self):
        return "Every message sent by Insight consumes a ticket. Consumed tickets become available again " \
               "after a set interval. If all tickets are consumed then Insight " \
               "will wait for a ticket to become available again.\nEach Discord server has an allocated number " \
               "of tickets to provide service fairness. Servers running a large number of feeds that spam " \
               "kills will be heavily rate limited to provide availability for servers with less active " \
               "feeds.\nRate limits are chained meaning a channel message is first limited by a channel limiter and " \
               "then a separate server limiter.\n\n\nWhat to do if you are reaching the rate limit regularly:" \
               "\n\n* Reduce the number of feeds on your Discord server or change the settings of your feeds to reduce " \
               "the number of mails posted.\n\n* Host Insight yourself and set your own rate limits to provide " \
               "dedicated service. [Insight Wiki on self-hosting](https://wiki.eveinsight.net/install)\n\n" \
               "Additional resources regarding rate limit mechanics are available on the wiki. " \
               "[Rate Limits Wiki](https://wiki.eveinsight.net/user/limits)."

    async def get_embed(self, d_message: discord.Message, message_text: str, **kwargs) -> discord.Embed:
        e = discord.Embed()
        e.color = discord.Color(659493)
        e.timestamp = datetime.datetime.utcnow()
        e.set_author(name=self.__class__.__name__)
        e.description = self.header()
        no_redact = self.service.is_admin(d_message.author.id)
        for l in await self.get_limiters(d_message, no_redact):
            limiter_name = "Limiter for {}".format(l.get("name"))
            f_body = "Tickets remaining: {} ({}%)\n".format(l.get("available"), l.get("remaining_ratio"))
            f_body += "Tickets used: {} ({}%)\n".format(l.get("used_tickets"), l.get("usage_ratio"))
            f_body += "Tickets allocated: {}\n".format(l.get("allocation"))
            f_body += "Tickets cooldown interval: {} seconds\n".format(l.get("interval"))
            f_body += "Queue Length: {} tickets".format(l.get("queue_length"))
            e.add_field(name=limiter_name, value=f_body, inline=False)
        e.set_footer(text='Utility command')
        return e

    async def get_text(self, d_message: discord.Message, message_text: str, **kwargs) -> str:
        t = "{}\n\n\n".format(self.header())
        no_redact = self.service.is_admin(d_message.author.id)
        for l in await self.get_limiters(d_message, no_redact):
            t += "Limiter for {}\n".format(l.get("name"))
            t += "Tickets remaining: {} ({}%)\n".format(l.get("available"), l.get("remaining_ratio"))
            t += "Tickets used: {} ({}%)\n".format(l.get("used_tickets"), l.get("usage_ratio"))
            t += "Tickets allocated: {}\n".format(l.get("allocation"))
            t += "Tickets cooldown interval: {} seconds\n".format(l.get("interval"))
            t += "Queue Length: {} tickets\n\n".format(l.get("queue_length"))
        return t


