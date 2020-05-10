from swagger_client.rest import ApiException
import swagger_client
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from multiprocessing.pool import ThreadPool
from database.db_tables import Base as dec_Base
import datetime
from typing import List
import concurrent.futures


class sde_impoter(object):
    @classmethod
    def make_from_sde(cls,__row):
        raise NotImplementedError

    @classmethod
    def get_missing_ids(cls,service_module,sde_session,sde_base):
        raise NotImplementedError

    @classmethod
    def get_query_filter(cls,sde_base):
        raise NotImplementedError

    @classmethod
    def import_all_sde(cls,service_module,sde_session,sde_base):
        db: Session = service_module.get_session()
        try:
            missing_ids = cls.get_missing_ids(service_module,sde_session,sde_base)
            length_missing_ids = len(missing_ids)
            if length_missing_ids > 0:
                print("Insight needs to import {} {} from the SDE. Importing now...".format(str(length_missing_ids),
                                                                                            cls.__name__))
            else:
                print("No {} to import".format(cls.__name__))
                return
            for chunk in name_only.split_lists(missing_ids, 75000):
                start = datetime.datetime.utcnow()
                try:
                    for sde_id in chunk:
                        try:
                            __row = sde_session.query(sde_base).filter(cls.get_query_filter(sde_base) == sde_id).one()
                            if cls.session_exists(sde_id, db):
                                new_row = cls.make_from_sde(__row)
                                new_row.load_fk_objects()
                                db.merge(new_row)
                            else:
                                new_row = cls.make_from_sde(__row)
                                new_row.session_add_nonexists_fk(db)
                                db.add(new_row)
                        except Exception as ex:
                            print(ex)
                            raise ex
                    db.commit()
                    print("Imported {} {} from the SDE in {} seconds".format(str(len(chunk)),cls.__name__,str((datetime.datetime.utcnow() - start).total_seconds())))
                except Exception as ex:
                    print(ex)
                    db.rollback()
        except Exception as ex:
            print(ex)
            db.rollback()
            sde_session.rollback()
        finally:
            db.close()
            sde_session.close()


from .base_objects import name_only
from .locations import Locations