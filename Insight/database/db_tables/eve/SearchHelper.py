from sqlalchemy.orm import Session
import InsightExc
from database.db_tables.eve import tb_types, tb_groups, tb_categories
from sqlalchemy import or_


class SearchHelper(object):
    @classmethod
    def search(cls, db_session: Session, table, col_match, search_str, limit=400):
        if db_session.query(table).filter(col_match.ilike("%{}%".format(search_str))).count() > limit:
            raise InsightExc.userInput.TooManyOptions
        else:
            return db_session.query(table).filter(col_match.ilike("%{}%".format(search_str))).all()

    @classmethod
    def search_type_group_is_ship(cls, db_session: Session, search_str):
        """returns a list of combined types and groups matching the queried name or that belong to ship or structure category"""
        limit = 400
        s = "%{}%".format(search_str)
        results = db_session.query(tb_types). \
            join(tb_types.object_group). \
            join(tb_groups.object_category). \
            filter(or_(tb_types.type_name.ilike(s), tb_types.type_id.ilike(s))). \
            filter(tb_categories.category_id == 6). \
            limit(limit). \
            all()
        results += db_session.query(tb_groups). \
            join(tb_groups.object_category). \
            filter(or_(tb_groups.name.ilike(s), tb_groups.group_id.ilike(s))). \
            filter(tb_categories.category_id == 6). \
            limit(limit - len(results)). \
            all()
        return results
