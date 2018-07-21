from . import InsightException


class Cancel(InsightException):
    """User canceled input"""

    def __init__(self, message="Canceled"):
        super().__init__(message)


class NotInteger(InsightException):
    def __init__(self, message=""):
        super().__init__(message)
