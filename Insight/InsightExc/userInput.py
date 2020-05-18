from . import InsightException


class Cancel(InsightException):
    """User canceled input"""

    def __init__(self, message="Canceled"):
        super().__init__(message)


class NotInteger(InsightException):
    def __init__(self, message=""):
        super().__init__(message)


class BitLengthExceeded(InsightException):
    def __init__(self, message="You entered an invalid number that is not recognized by Insight since it is too big."):
        super().__init__(message)


class InvalidIndex(InsightException):
    def __init__(self, message="You entered an invalid index."):
        super().__init__(message)


class InputTimeout(InsightException):
    def __init__(self, message="You took too long to respond."):
        super().__init__(message)


class InsightProgrammingError(InsightException):
    def __init__(self, message="One of the assertions for the option container failed. This is a programming error"):
        super().__init__(message)


class TooManyOptions(InsightException):
    def __init__(self, message="There are too many options to show! If you are searching please refine your search. "
                               "Ensure Insight has the 'Embed Links' role in this channel as more options can be "
                               "displayed through Discord rich embeds."):
        super().__init__(message)


class NewDMError(InsightException):
    def __init__(self, message="Unable to open a DM. Ensure you can receive direct messages from Insight."):
        super().__init__(message)


class NotFloat(InsightException):
    def __init__(self, message="You entered an invalid number."):
        super().__init__(message)


class CommandNotFound(InsightException):
    def __init__(self, message="Command not found."):
        super().__init__(message)


class ShortSearchCriteria(InsightException):
    def __init__(self, min_length=2, message=""):
        if not message:
            message = "The minimum search length is {} characters. Please refine your search.".format(min_length)
        super().__init__(message)


class InvalidInput(InsightException):
    def __init__(self, message="Invalid input."):
        super().__init__(message)


class EmbedPermissionRequired(InsightException):
    def __init__(self, message="This function requires Discord 'embed links' permissions to function and will "
                               "not function in text-only mode.\n\n"
                               "See https://support.discord.com/hc/en-us/sections/202856377-Permissions "
                               "for assistance with permissions."):
        super().__init__(message)
