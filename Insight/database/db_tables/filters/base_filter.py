from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import scoped_session, Session, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import *
from sqlalchemy import *
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from multiprocessing.pool import ThreadPool
from database.db_tables import Base as dec_Base
from typing import List
from ..discord import discord_channels
import enum


class mention_method(enum.Enum):
    noMention = ''
    here = '@here'
    everyone = '@everyone'


class listTypeEnum(enum.Enum):
    blacklist = 'blacklist'
    whitelist = 'whitelist'
    nolist = 'nolist'


class filter_base(object):
    def load_fk_objects(self):
        pass

    def set_blacklist(self):
        self.list_type = listTypeEnum.blacklist

    def set_whitelist(self):
        self.list_type = listTypeEnum.whitelist

    def set_nolist(self):
        self.list_type = listTypeEnum.nolist

    def __str__(self):
        return str(self.object_item)

    @classmethod
    def get_row(cls, channel_id, filter_id, service_module):
        db: Session = service_module.get_session()
        try:
            __row = db.query(cls).filter(cls.channel_id == channel_id, cls.filter_id == filter_id).one()
            return __row
        except NoResultFound:
            __row = cls(filter_id,channel_id)
            return __row

    @classmethod
    def get_remove(cls,channel_id,filter_id,service_module):
        db:Session = service_module.get_session()
        try:
            __row = db.query(cls).filter(cls.channel_id == channel_id, cls.filter_id == filter_id).one()
            db.delete(__row)
        except NoResultFound:
            pass
        except Exception as ex:
            print(ex)


