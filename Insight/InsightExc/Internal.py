from . import InsightException


class VisualAppearanceNotEquals(InsightException):

    def __init__(self, message="Mismatch visuals"):
        super().__init__(message)


class ThreadPauseExc(InsightException):
    def __init__(self, message=""):
        super().__init__(message)


class ThreadPauseTimeout(ThreadPauseExc):

    def __init__(self, message="ThreadPause Timeout"):
        super().__init__(message)


