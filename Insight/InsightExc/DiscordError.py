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


class UnboundFeed(InsightException):
    def __init__(self, message="Unbound feed"):  # todo
        super().__init__(message)


class NonFatalExit(InsightException):
    def __init__(self, message="Missing error text"):  # todo
        super().__init__(message)


class LackPermission(InsightException):
    def __init__(self, message="Unauthorized"):  # todo
        super().__init__(message)
