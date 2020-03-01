import discord
import InsightLogger
import InsightExc


class DiscordPermissionCheck(object):
    logger = InsightLogger.InsightLogger.get_logger('PermissionCheck', 'PermissionCheck.log', console_print=True)

    @classmethod
    def is_dm(cls, discord_object):
        return isinstance(discord_object, discord.DMChannel) or isinstance(discord_object, discord.GroupChannel)

    @classmethod
    def get_permissions(cls, discord_object) -> discord.Permissions:
        try:
            if isinstance(discord_object, discord.Message):
                if cls.is_dm(discord_object.channel):
                    raise InsightExc.Internal.DiscordDMUser
                return discord_object.channel.permissions_for(discord_object.channel.guild.me)
            elif cls.is_dm(discord_object):
                raise InsightExc.Internal.DiscordDMUser
            elif isinstance(discord_object, discord.TextChannel):
                return discord_object.permissions_for(discord_object.guild.me)
            else:
                cls.logger.error("Unable to perform get_permissions for object of type: {}".format(type(discord_object)))
        except InsightExc.Internal.DiscordDMUser as ex:
            raise ex
        except Exception as ex:
            cls.logger.error("EX: {} getting permission".format(str(ex)))
            raise ex

    @classmethod
    def can_text(cls, discord_object):
        try:
            p: discord.Permissions = cls.get_permissions(discord_object)
        except InsightExc.Internal.DiscordDMUser:
            return True
        return p.send_messages

    @classmethod
    def can_embed(cls, discord_object):
        try:
            p: discord.Permissions = cls.get_permissions(discord_object)
        except InsightExc.Internal.DiscordDMUser:
            return True
        return p.embed_links and p.send_messages
