from .TempBase import *


class IntJoin(dec_Base.Base, TempBase):
    __tablename__ = 'tmp_intjoin'
    no_pk = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    key = Column(Integer, index=True, nullable=False, autoincrement=False)
    epoch = Column(Integer, index=True, nullable=False, autoincrement=False)
    int_field = Column(Integer, index=False, nullable=False, autoincrement=False)

    def __init__(self, key: int, epoch: int, int_field: int):
        self.key = key
        self.epoch = epoch
        self.int_field = int_field
