from .discord_base import *
from ..eve import tb_alliances

class Channels(dec_Base.Base,discord_channel_base):
    __tablename__ = 'discord_channels'

    channel_id = Column(BIGINT,primary_key=True,nullable=False,autoincrement=False)
    feed_running = Column(Boolean,default=False,nullable=False)
    channel_name = Column(String,default="",nullable=False)

    object_capRadar = relationship("CapRadar", uselist=False,cascade="delete", back_populates="object_channel",lazy="joined")
    object_enFeed = relationship("EnFeed",uselist=False,cascade="delete",back_populates="object_channel",lazy="joined")
    object_filter_alliances = relationship("Filter_alliances",uselist=True,cascade="delete",back_populates="object_channel",
                                       lazy="joined")
    object_filter_corporations = relationship("Filter_corporations", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_characters = relationship("Filter_characters ", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_categories = relationship("Filter_categories", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_groups = relationship("Filter_groups", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_types = relationship("Filter_types", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_regions = relationship("Filter_regions", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")
    object_filter_systems = relationship("Filter_systems", uselist=True, cascade="delete", back_populates="object_channel",
                                       lazy="joined")

    def __init__(self, object_id):
        self.channel_id = object_id

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id

    @classmethod
    def commit_list_entry(cls,eve_object:tb_alliances,channel_id,service_module):
        db:Session = service_module.get_session()
        try:
            if isinstance(eve_object, tb_alliances):
                db.merge(tb_Filter_alliances(eve_object.get_id(), channel_id))
            if isinstance(eve_object,tb_corporations):
                db.merge(tb_Filter_corporations(eve_object.get_id(),channel_id))
            if isinstance(eve_object,tb_characters):
                db.merge(tb_Filter_characters(eve_object.get_id(),channel_id))
            db.commit()
            return "ok"
        except IntegrityError:
            return "This entity has already been added previously"
        except Exception as ex:
            print(ex)
            return str(ex)
        finally:
            db.close()


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

from ..filters import *
from ..eve import *