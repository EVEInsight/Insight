from swagger_client.rest import ApiException
import swagger_client
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from multiprocessing.pool import ThreadPool
import datetime
from database.db_tables import Base as dec_Base
from sqlalchemy.exc import *
import enum
from ..eve import *


class contact_owner(enum.Enum):
    pilot = 'pilot'
    corp = 'corp'
    alliance = 'alliance'

    def __gt__(self, other):
        return False

    def __lt__(self, other):
        return False


class sso_base(object):
    def get_id(self):
        raise NotImplementedError

    def load_fk_objects(self, service_module):
        pass
