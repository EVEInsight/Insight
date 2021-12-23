from .base_objects import *
import datetime
import traceback
from InsightUtilities import DBSessions
import json
import InsightExc
import random
import string


class InsightMeta(dec_Base.Base):
    __tablename__ = 'insight_meta'

    key = Column(String, primary_key=True, index=True, nullable=False, autoincrement=False)
    modified = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False, index=True)
    access = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False, index=True)
    value = Column(Text, nullable=False)

    def __init__(self, option_key: str, option_value_dict: dict):
        self.key = str(option_key)
        self.value = json.dumps(option_value_dict)
        self.access = datetime.datetime.utcnow()
        self.modified = datetime.datetime.utcnow()

    def _set_value(self, set_dict: dict):
        self.value = json.dumps(set_dict)
        self.update_modified_time()

    def _get_value(self):
        return json.loads(self.value)

    def update_access_time(self):
        self.access = datetime.datetime.utcnow()

    def update_modified_time(self):
        self.modified = datetime.datetime.utcnow()

    def get_json(self):
        return {
            "key": self.key,
            "data": self._get_value(),
            "modified": self.modified,
            "access": self.access
        }

    @classmethod
    def get(cls, key_value) -> dict:
        db: Session = DBSessions().get_session()
        try:
            row: cls = db.query(cls).filter(cls.key == key_value).one_or_none()
            if row is None:
                default_val = cls.default_key_pairs().get(key_value)
                if default_val is None:
                    print("Error attempting to get non-default config value.")
                    raise InsightExc.GeneralException.ProgrammingError
                else:
                    row = cls(key_value, default_val)
                    db.add(row)
                    db.commit()
                    return row.get_json()
            else:
                row.update_access_time()
                db.commit()
                return row.get_json()
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            db.close()

    @classmethod
    def set(cls, key_value: str, option_dict: dict) -> bool:
        db: Session = DBSessions().get_session()
        try:
            row = db.query(cls).filter(cls.key == key_value).one_or_none()
            if row is None:
                row = cls(key_value, option_dict)
                db.add(row)
            else:
                row._set_value(option_dict)
            db.commit()
            return True
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            return False
        finally:
            db.close()

    @classmethod
    def delete(cls, key_value: str) -> bool:
        """deletes the key"""
        db: Session = DBSessions().get_session()
        try:
            row = db.query(cls).filter(cls.key == key_value).one_or_none()
            if row is None:
                return True
            else:
                db.delete(row)
            db.commit()
            return True
        except Exception as ex:
            print(ex)
            traceback.print_exc()
            return False
        finally:
            db.close()

    @classmethod
    def default_key_pairs(cls) -> dict:
        return {
            "motd": {"value": ""},
            "zk_identifier": {"value": "".join(random.choice(string.ascii_lowercase) for x in range(15))},
            "last_reimport_locations":      {"value": str(datetime.datetime.utcnow())},
            "last_reimport_types":          {"value": str(datetime.datetime.utcnow())},
            "last_reimport_groups":         {"value": str(datetime.datetime.utcnow())},
            "last_reimport_categories":     {"value": str(datetime.datetime.utcnow())},
            "last_reimport_stargates":      {"value": str(datetime.datetime.utcnow())},
            "last_reimport_systems":        {"value": str(datetime.datetime.utcnow())},
            "last_reimport_constellations": {"value": str(datetime.datetime.utcnow())},
            "last_reimport_regions":        {"value": str(datetime.datetime.utcnow())},
            "last_reimport_characters":     {"value": str(datetime.datetime.utcnow())},
            "last_reimport_corporations":   {"value": str(datetime.datetime.utcnow())},
            "last_reimport_alliances":      {"value": str(datetime.datetime.utcnow())}
        }

