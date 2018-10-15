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
    def __init__(self, message="Lock timeout"):  # todo
        super().__init__(message)
