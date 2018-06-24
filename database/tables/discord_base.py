from database.Base import Base
from database.tables import *
import database.tables
from swagger_client.rest import ApiException
from swagger_client import Configuration
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship, backref
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship, backref
from sqlalchemy.inspection import inspect
from sqlalchemy import *
import swagger_client
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import dateparser
from multiprocessing.pool import ThreadPool


class discord_channel_base(object):
    def load_fk_objects(self):
        pass

    @classmethod
    def primary_key_row(cls):
        raise NotImplementedError

    @classmethod
    def get_row(cls,id,service_module):
        db: Session = service_module.get_session()
        try:
            __row = db.query(cls).filter(cls.primary_key_row()==id).one()
            return __row
        except NoResultFound:
            __row = cls(id)
            return __row
        finally:
            db.close()

    @classmethod
    def make_row(cls,id,service_module):
        if not cls.exists(id,service_module):
            db: Session = service_module.get_session()
            try:
                db.merge(cls(id))
                db.commit()
                return True
            except Exception as ex:
                print(ex)
                return False
            finally:
                db.close()
        else:
            return True

    @classmethod
    def exists(cls,id,service_module):
        db: Session = service_module.get_session()
        try:
            db.query(cls).filter(cls.primary_key_row() == id).one()
            return True
        except NoResultFound:
            return False
        finally:
            db.close()