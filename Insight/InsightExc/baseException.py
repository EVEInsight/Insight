class InsightException(Exception):
    def __init__(self, message="Missing error message"):
        super(InsightException, self).__init__(message)
