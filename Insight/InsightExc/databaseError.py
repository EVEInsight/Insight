from . import InsightException


class DatabaseError(InsightException):
    """Error saving data to the database"""

    def __init__(self, message="Database error"):
        super().__init__(message)

