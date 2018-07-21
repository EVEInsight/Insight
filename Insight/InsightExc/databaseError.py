from . import InsightException


class SaveData(InsightException):
    """Error saving data to the database"""

    def __init__(self, message):
        super().__init__(message)
