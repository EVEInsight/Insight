from . import InsightException


class ProgrammingError(InsightException):

    def __init__(self, message="Error in programing. Unexpected."):
        super().__init__(message)