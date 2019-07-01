from .base_objects import *
import datetime
import traceback


class InsightMeta(dec_Base.Base):
    __tablename__ = 'insight_meta'

    option_key = Column(String, primary_key=True, nullable=False, autoincrement=False)
    option_value = Column(String, nullable=False)

    def __init__(self, option_key: str, option_value: str):
        self.option_key = str(option_key)
        self.option_value = str(option_value)

    @classmethod
    def get_value(cls, key_value, service_module):
        db: Session = service_module.get_session()
        try:
            row = db.query(cls).filter(cls.option_key == key_value).one()
            return row.option_value
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            db.close()

    @classmethod
    def set_value(cls, key_value, option_value, service_module):
        db: Session = service_module.get_session()
        try:
            row = db.query(cls).filter(cls.option_key == key_value).one()
            row.option_value = str(option_value)
            db.commit()
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            db.close()

    @classmethod
    def default_key_pairs(cls) -> dict:
        return {
            "the_watcher_last_full_pull": datetime.datetime.utcnow() - datetime.timedelta(days=365)
        }

    @classmethod
    def set_default_values(cls, db_session):
        db: Session = db_session
        try:
            for key, val in cls.default_key_pairs().items():
                if not db.query(cls).filter(cls.option_key == key).one_or_none():
                    db.add(cls(key, val))
                    print("Setting Insight meta variable '{}' = '{}'".format(str(key), str(val)))
            db.commit()
        except Exception as ex:
            traceback.print_exc()
            print(ex)
        finally:
            db.close()
