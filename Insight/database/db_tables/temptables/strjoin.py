from .TempBase import *


class StrJoin(dec_Base.Base, TempBase):
    __tablename__ = 'tmp_strjoin'
    no_pk = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    key = Column(Integer, index=True, nullable=False, autoincrement=False)
    epoch = Column(Integer, index=True, nullable=False, autoincrement=False)
    str_field = Column(String, index=False, nullable=False)

    def __init__(self, key: int, epoch: int, str_field: str):
        self.key = key
        self.epoch = epoch
        self.str_field = str_field
