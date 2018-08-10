from . import InsightException


class VisualAppearanceNotEquals(InsightException):

    def __init__(self, message="Mismatch visuals"):
        super().__init__(message)
