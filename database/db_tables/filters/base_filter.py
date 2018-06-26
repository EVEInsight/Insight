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
