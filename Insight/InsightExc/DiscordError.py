from . import InsightException


class DiscordPermissions(InsightException):
    def __init__(self, message="Permission error. Insight is unable to post a message due to incorrect permissions."):
        super().__init__(message)


class MessageMaxRetryExceed(InsightException):
    def __init__(self, message="Max retry exceeded for message."):
        super().__init__(message)


class ChannelLoaderError(InsightException):
    def __init__(self, message="Fatal error when attempting to load your channel feed. Contact Insight admin for help."):
        super().__init__(message)


class LockTimeout(InsightException):
    def __init__(self):
        msg = "Another user is currently running a command in this feed or the feed is currently busy. " \
              "Try running this command once the current active task is complete. Run the '!limits' command to check " \
              "your current channel and server rate limits if you notice a significant slowdown or delay."
        super().__init__(msg)


class UnboundFeed(InsightException):
    def __init__(self):
        msg = "This feed has been removed. You are unable to make changes to a deallocated feed."
        super().__init__(msg)


class NonFatalExit(InsightException):
    def __init__(self, message="Missing error text"):  # todo
        super().__init__(message)


class LackChannelPermission(InsightException):
    def __init__(self):
        msg = "You are unauthorized to use this command in this channel. This channel is potentially locked by " \
              "a feed user. You must have at least one of the following Discord channel/server roles to execute " \
              "this command:\n\nAdministrator\nManage Roles\nManage Messages\nManage Guild\nManage Channel" \
              "\nManage webhooks\n\nYou can request a channel moderator with one of these roles to remove " \
              "the restriction by granting you one of these roles. The moderator can remove this restriction for " \
              "all channel users by executing the '!unlock' command. Receiving this error in a private message " \
              "indicates the command is not supported in direct messages."
        super().__init__(msg)


class LackInsightAdmin(InsightException):
    def __init__(self, user_id=None):
        msg = "You are unauthorized to execute this command as you are not an Insight super admin. Execution of this " \
              "command requires your Discord user ID: '{}' to be in the 'InsightAdmins.txt' file. This file is " \
              "located next to your 'config.ini' file. You may execute this command after editing the file " \
              "and restarting Insight.".format(str(user_id))
        super().__init__(msg)


class FeedConvertReload(InsightException):
    def __init__(self):
        super().__init__('Feed reload after conversion.')


class EmbedOptionsError(InsightException):
    def __init__(self):
        super().__init__('Embed options error')


class QueueDelayInvalidatesFilter(InsightException):
    def __init__(self):
        super().__init__('The message is invalid as it has been in the queue too long and fails the time condition'
                         'filters now.')
