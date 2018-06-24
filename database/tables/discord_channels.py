from database.tables.discord_base import *
from database.tables import *


class Channels(Base,discord_channel_base):
    __tablename__ = 'channels'

    channel_id = Column(BIGINT,primary_key=True,nullable=False,autoincrement=False)
    feed_running = Column(Boolean,default=False,nullable=False)
    channel_name = Column(String,default="",nullable=False)

    object_capRadars = relationship("CapRadar", uselist=True,cascade="delete", back_populates="object_channel")

    def __init__(self, object_id):
        self.channel_id = object_id

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id

    @classmethod
    def set_feed_running(cls,channel_id,value:bool,service_module):
        __row = cls.get_row(channel_id,service_module)
        __row.feed_running = value
        service_module.get_session().merge(__row)
        try:
            service_module.get_session().commit()
        except Exception as ex:
            print(ex)
            service_module.get_session().rollback()
        finally:
            service_module.get_session().close()