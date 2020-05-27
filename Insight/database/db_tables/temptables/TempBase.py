from database.db_tables import Base as dec_Base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, ForeignKey, Index, String
import time
import random


class TempBase(object):
    @classmethod
    def get_epoch(cls):
        return int(time.time())

    @classmethod
    def get_random_key(cls):
        return random.randint(1, int(9e+8))

    @classmethod
    def clear_tmp_table(cls, db: Session):
        db.query(cls).delete()
        db.commit()
