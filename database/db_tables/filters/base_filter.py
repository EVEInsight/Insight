from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from multiprocessing.pool import ThreadPool
from database.db_tables import Base as dec_Base
from typing import List
import enum


class filter_base(object):
    pass


class mention_method(enum.Enum):
    noMention = ''
    here = '@here'
    everyone = '@everyone'