from . import InsightException


class Cancel(InsightException):
    """User canceled input"""

    def __init__(self, message="Canceled"):
        super().__init__(message)


class NotInteger(InsightException):
    def __init__(self, message=""):
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
    def __init__(self, message="There are too many options to show! If you are searching, please refine your search."):
        super().__init__(message)


class NewDMError(InsightException):
    def __init__(self, message="Unable to open a DM. Ensure you can receive direct messages from Insight."):
        super().__init__(message)
