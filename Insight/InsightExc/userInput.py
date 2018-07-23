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
