from . import InsightException


class Utilities(InsightException):
    pass


class EmbedMaxTotalCharLimit(InsightException):
    def __init__(self, message="Rich embed char limit exceeded."):
        super().__init__(message)


class EmbedItemCharLimit(InsightException):
    def __init__(self, item_length: int = 0, max_length: int = 0):
        message = "A an exceeded its max length and could not be displayed. Length of item: {} -" \
                  " Max length: {}".format(item_length, max_length)
        super().__init__(message)


class EmbedMaxTotalFieldsLimit(InsightException):
    def __init__(self, message="Rich embed field total limit exceeded."):
        super().__init__(message)
