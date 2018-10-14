from sqlalchemy import *
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from . import sqlUpdater
from distutils.version import LooseVersion
from sqlalchemy.ext.declarative import declarative_base
import sys

versionBase = declarative_base()


class Version(versionBase):
    __tablename__ = 'version'

    row = Column(Integer, default=0, primary_key=True, autoincrement=False, nullable=False)
    database_version = Column(String, default='v0.10.0', nullable=False)

    def __init__(self):
        self.set_version()

    def set_version(self):
        self.database_version = str(service.ServiceModule.get_db_version())

    def get_version(self):
        return LooseVersion(self.database_version)

    @classmethod
    def make_version(cls, ses_obj, engine):
        assert isinstance(ses_obj, Session)
        try:
            row = ses_obj.query(cls).filter(cls.row == 0).one()
        except NoResultFound:
            row = cls()
        updater = sqlUpdater.sqlUpdater(engine, row.get_version())
        tu = updater.update_all()
        row.database_version = tu[0]
        ses_obj.merge(row)
        try:
            ses_obj.commit()
            if tu[1]:
                print("An error occurred when modifying the tables.")
                sys.exit(1)
        except Exception as ex:
            print(ex)
            sys.exit(1)


import service
