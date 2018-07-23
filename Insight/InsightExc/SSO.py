from . import InsightException


class SSOerror(InsightException):
    """Error getting SSO"""

    def __init__(self, message="SSO Error"):
        super().__init__(message)
