from . import InsightException


class BaseRedis(InsightException):
    pass


class NoRedis(BaseRedis):
    def __init__(self):
        super().__init__('This function requires a Redis instance. Ask your Insight server administrator to connect '
                         'Insight to a Redis instance.')


class KeyDoesNotExist(BaseRedis):
    pass
