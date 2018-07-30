from .discord_base import *
from ..eve import tb_alliances
import InsightExc


class Channels(dec_Base.Base,discord_channel_base):
    __tablename__ = 'discord_channels'

    channel_id = Column(BIGINT,primary_key=True,nullable=False,autoincrement=False)
    feed_running = Column(Boolean,default=False,nullable=False)
    channel_name = Column(String,default="",nullable=False)

    object_capRadar = relationship("CapRadar", uselist=False, cascade="delete", back_populates="object_channel",
                                   lazy="subquery")
    object_enFeed = relationship("EnFeed", uselist=False, cascade="delete", back_populates="object_channel",
                                 lazy="subquery")
    object_tokens = relationship("Discord_Tokens", uselist=True, cascade="delete", back_populates="object_channel")
    object_filter_alliances = relationship("Filter_alliances", uselist=True,
                                           cascade="save-update, merge, delete, delete-orphan",
                                           back_populates="object_channel", lazy="subquery")
    object_filter_corporations = relationship("Filter_corporations", uselist=True,
                                              cascade="save-update, merge, delete, delete-orphan",
                                              back_populates="object_channel", lazy="subquery")
    object_filter_characters = relationship("Filter_characters", uselist=True,
                                            cascade="save-update, merge, delete, delete-orphan",
                                            back_populates="object_channel", lazy="subquery")
    object_filter_categories = relationship("Filter_categories", uselist=True,
                                            cascade="save-update, merge, delete, delete-orphan",
                                            back_populates="object_channel", lazy="subquery")
    object_filter_groups = relationship("Filter_groups", uselist=True,
                                        cascade="save-update, merge, delete, delete-orphan",
                                        back_populates="object_channel", lazy="subquery")
    object_filter_types = relationship("Filter_types", uselist=True,
                                       cascade="save-update, merge, delete, delete-orphan",
                                       back_populates="object_channel", lazy="subquery")
    object_filter_regions = relationship("Filter_regions", uselist=True,
                                         cascade="save-update, merge, delete, delete-orphan",
                                         back_populates="object_channel", lazy="subquery")
    object_filter_systems = relationship("Filter_systems", uselist=True,
                                         cascade="save-update, merge, delete, delete-orphan",
                                         back_populates="object_channel", lazy="subquery")

    def __init__(self, object_id):
        self.channel_id = object_id

    @classmethod
    def primary_key_row(cls):
        return cls.channel_id

    @classmethod
    def reset_filters(cls, ch_id, service_module):
        db: Session = service_module.get_session()
        try:
            row: cls = db.query(cls).filter(cls.channel_id == ch_id).one()
            row.object_filter_alliances = []
            row.object_filter_corporations = []
            row.object_filter_characters = []
            row.object_filter_categories = []
            row.object_filter_groups = []
            row.object_filter_types = []
            row.object_filter_regions = []
            row.object_filter_systems = []
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    @classmethod
    def commit_list_entry(cls,eve_object:tb_alliances,channel_id,service_module,**kwargs):
        db:Session = service_module.get_session()
        try:
            if isinstance(eve_object, tb_alliances):
                db.merge(tb_Filter_alliances.get_row(channel_id=channel_id,filter_id=eve_object.get_id(),service_module=service_module))
            if isinstance(eve_object,tb_corporations):
                db.merge(tb_Filter_corporations.get_row(channel_id=channel_id,filter_id=eve_object.get_id(),service_module=service_module))
            if isinstance(eve_object,tb_characters):
                db.merge(tb_Filter_characters.get_row(channel_id=channel_id,filter_id=eve_object.get_id(),service_module=service_module))
            if isinstance(eve_object,tb_systems):
                __row = tb_Filter_systems.get_row(channel_id=channel_id,filter_id=eve_object.get_id(),service_module=service_module)
                __row.max = kwargs.get("maxly")
                db.merge(__row)
            db.commit()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
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

    def delete_all_contacts(self, service_module):
        db: Session = service_module.get_session()

        def helper(table):
            for i in table:
                db.delete(i)

        helper(self.object_filter_characters)
        helper(self.object_filter_corporations)
        helper(self.object_filter_alliances)

    def str_tokens(self):
        if len(self.object_tokens) > 0:
            return_str = "This channel is now synced with the following tokens:\n\n"
            for t in self.object_tokens:
                return_str += str(t) + '\n\n'
            return return_str
        else:
            return "This radar feed has no synced contact tokens. Contact tokens block your allies from " \
                   "appearing as potential targets in a radar feed. You can add a token by running the command '!sync'."

    def sync_api_contacts(self, service_module):
        db: Session = service_module.get_session()
        try:
            _pilots = []
            _corps = []
            _alliances = []
            for token in self.object_tokens:
                _pilots += [p for p in token.get_all_pilot_ids()]
                _corps += [c for c in token.get_all_corp_ids()]
                _alliances += [a for a in token.get_all_alliance_ids()]
            self.object_filter_characters = []
            self.object_filter_corporations = []
            self.object_filter_alliances = []
            db.flush()
            for p in list(set(_pilots)):
                self.object_filter_characters.append(
                    tb_Filter_characters(p, discord_channel_id=self.channel_id, load_fk=False))
            for c in list(set(_corps)):
                self.object_filter_corporations.append(
                    tb_Filter_corporations(c, discord_channel_id=self.channel_id, load_fk=False))
            for a in list(set(_alliances)):
                self.object_filter_alliances.append(
                    tb_Filter_alliances(a, discord_channel_id=self.channel_id, load_fk=False))
        except Exception as ex:
            print(ex)


from ..filters import *
from ..eve import *