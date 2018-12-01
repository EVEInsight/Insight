from sqlalchemy.orm import Session
import InsightExc


class SearchHelper(object):
    @classmethod
    def search(cls, db_session: Session, table, col_match, search_str, limit=400):
        if db_session.query(table).filter(col_match.ilike("%{}%".format(search_str))).count() > limit:
            raise InsightExc.userInput.TooManyOptions
        else:
            return db_session.query(table).filter(col_match.ilike("%{}%".format(search_str))).all()

