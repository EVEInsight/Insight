from .discord_base import *


class Channels(dec_Base.Base,discord_channel_base):
    __tablename__ = 'channels'

    channel_id = Column(BIGINT,primary_key=True,nullable=False,autoincrement=False)
    feed_running = Column(Boolean,default=False,nullable=False)
    channel_name = Column(String,default="",nullable=False)

    object_capRadar = relationship("CapRadar", uselist=False,cascade="delete", back_populates="object_channel")
    object_bl_alliances = relationship("BL_alliances",uselist=True,cascade="delete",back_populates="object_channel",
                                       lazy="joined")
    object_bl_corporations = relationship("BL_corporations", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_characters = relationship("BL_characters ", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_categories = relationship("BL_categories", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_groups = relationship("BL_groups", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_types = relationship("BL_types", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_regions = relationship("BL_regions", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_bl_systems = relationship("BL_systems", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_alliances = relationship("WL_alliances",uselist=True,cascade="delete",back_populates="object_channel",
                                       lazy="joined")
    object_wl_corporations = relationship("WL_corporations", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_characters = relationship("WL_characters ", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_categories = relationship("WL_categories", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_groups = relationship("WL_groups", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_types = relationship("WL_types", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_regions = relationship("WL_regions", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_wl_systems = relationship("WL_systems", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")

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