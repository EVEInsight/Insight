from .InsightSingleton import InsightSingleton
from sqlalchemy.orm import scoped_session, Session


class DBSessions(metaclass=InsightSingleton):
    def __init__(self, sc_session):
        self._sc_session: scoped_session = sc_session

    def get_session(self) -> Session:
        """

        :rtype: Session
        """
        session_object: Session = self._sc_session()
        assert isinstance(session_object, Session)
        return session_object
