from . import InsightException


class DiscordPermissions(InsightException):

    def __init__(self, message="Permission error. Insight is unable to post a message due to incorrect permissions."):
        super().__init__(message)
