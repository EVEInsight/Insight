from .sso_base import *
from ..eve import tb_alliances
import requests
import json
from requests.auth import HTTPBasicAuth
import swagger_client
import InsightExc
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine


def get_key():
    return service.ServiceModule.get_key()


class Tokens(dec_Base.Base, sso_base):
    __tablename__ = 'tokens'

    token_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    discord_user = Column(BIGINT, ForeignKey("discord_users.user_id"), nullable=False)
    refresh_token = Column(EncryptedType(String, get_key, AesEngine, 'pkcs5'), nullable=False)
    token = Column(EncryptedType(String, get_key, AesEngine, 'pkcs5'), nullable=True)
    character_id = Column(Integer, ForeignKey("characters.character_id"), nullable=True)
    corporation_id = Column(Integer, ForeignKey("corporations.corporation_id"), nullable=True)
    alliance_id = Column(Integer, ForeignKey("alliances.alliance_id"), nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    last_modified = Column(DateTime, default=datetime.datetime.utcnow(), nullable=False)
    etag_character = Column(String, nullable=True)
    etag_corp = Column(String, nullable=True)
    etag_alliance = Column(String, nullable=True)

    object_user = relationship("Users", uselist=False, back_populates="object_tokens")
    object_channels = relationship("Discord_Tokens", uselist=True, cascade="delete", back_populates="object_token")
    object_pilot = relationship("Characters", uselist=False, lazy="joined")
    object_corp = relationship("Corporations", uselist=False, lazy="joined")
    object_alliance = relationship("Alliances", uselist=False, lazy="joined")
    object_contacts_pilots = relationship("Contacts_Characters", cascade="save-update,merge,delete,delete-orphan",
                                          uselist=True,
                                          back_populates="object_token")
    object_contacts_corps = relationship("Contacts_Corporations", cascade="save-update,merge,delete,delete-orphan",
                                         uselist=True,
                                         back_populates="object_token")
    object_contacts_alliances = relationship("Contacts_Alliances", cascade="save-update,merge,delete,delete-orphan",
                                             uselist=True,
                                             back_populates="object_token")

    def __init__(self, discord_user, refresh_token):
        self.discord_user = discord_user
        self.refresh_token = refresh_token

    def __str__(self):
        syncs_with = "Pilot: {}\n".format(self.object_pilot.character_name) if self.object_pilot else ""
        syncs_with += "Corp: {}\n".format(self.object_corp.corporation_name) if self.object_corp else ""
        syncs_with += "Alliance: {}\n".format(self.object_alliance.alliance_name) if self.object_alliance else ""
        syncs_with += "Contains {} pilot, {} corp, and {} alliance contacts." \
            .format(str(len(self.object_contacts_pilots)), str(len(self.object_contacts_corps)),
                    str(len(self.object_contacts_alliances)))
        return syncs_with

    def str_mod(self):
        rst = "TokenID: {} Modified: {}\n".format(str(self.token_id), self.last_modified.replace(microsecond=0))
        rst += self.__str__()
        return rst

    def str_upd(self):
        rst = "TokenID: {} Updated: {}\n".format(str(self.token_id), self.last_updated.replace(microsecond=0))
        rst += self.__str__()
        return rst

    def str_wChcount(self):
        ch_count = "Discord channels using this token: {}".format(str(len(self.object_channels)))
        return "{}\n{}".format(self.str_upd(), ch_count)

    def get_affiliation(self, token, service_module):
        char_id = service_module.sso.get_char(token)
        if char_id:
            self.object_pilot = tb_characters(char_id)
            api = swagger_client.CharacterApi()
            api.api_client.set_default_header('User-Agent', "InsightDiscordKillfeeds")
            response = api.get_characters_character_id(character_id=char_id)
            if response.corporation_id:
                self.object_corp = tb_corporations(response.corporation_id)
            if response.alliance_id:
                self.object_alliance = tb_alliances(response.alliance_id)
        else:
            raise InsightExc.SSO.SSOerror

    def __alliance_api_call(self, api, **kwargs):
        return api.get_alliances_alliance_id_contacts_with_http_info(alliance_id=self.alliance_id, **kwargs)

    def __set_alliance_etag(self, new_etag):
        self.etag_alliance = new_etag

    def __corp_api_call(self, api, **kwargs):
        return api.get_corporations_corporation_id_contacts_with_http_info(corporation_id=self.corporation_id, **kwargs)

    def __set_corp_etag(self, new_etag):
        self.etag_corp = new_etag

    def __pilot_api_call(self, api, **kwargs):
        return api.get_characters_character_id_contacts_with_http_info(character_id=self.character_id, **kwargs)

    def __set_pilot_etag(self, new_etag):
        self.etag_character = new_etag

    def get_results(self, function_ptr, etag, new_etag_function_ptr):
        swagger_config = swagger_client.Configuration()
        swagger_config.access_token = self.token
        contacts_api = swagger_client.ContactsApi(swagger_client.ApiClient(swagger_config))
        r = function_ptr(contacts_api, datasource='tranquility', token=self.token, if_none_match=str(etag))
        __new_etag = r[2].get("Etag")
        number_pages = r[2].get("X-Pages")
        if number_pages is None:
            return r[0]
        else:
            r_items = [] + r[0]
            __index = 2
            while int(number_pages) >= __index:
                r_items += \
                self.__alliance_api_call(contacts_api, page=__index, datasource='tranquility', token=self.token)[0]
                __index += 1
            new_etag_function_ptr(__new_etag)
            return r_items

    def process_contact(self, contact, owner, service_module):
        if contact.contact_id == self.character_id or contact.contact_id == self.corporation_id or contact.contact_id == self.alliance_id:
            return  # prevent adding self
        elif contact.contact_type == "character":
            self.object_contacts_pilots.append(
                tb_contacts_pilots(contact.contact_id, owner, contact.standing, service_module))
        elif contact.contact_type == "corporation":
            self.object_contacts_corps.append(
                tb_contacts_corps(contact.contact_id, owner, contact.standing, service_module))
        elif contact.contact_type == "alliance":
            self.object_contacts_alliances.append(
                tb_contacts_alliances(contact.contact_id, owner, contact.standing, service_module))
        else:
            return

    def __remove(self, enum_owner, service_module):
        db: Session = service_module.get_session()
        def helper(table):
            rows = db.query(table).filter(table.token == self.token_id, table.owner == enum_owner)
            rows.delete()
        helper(tb_contacts_alliances)
        helper(tb_contacts_corps)
        helper(tb_contacts_pilots)

    def write_changes(self, api_call, etag, etag_function, enum_owner, service_module):
        try:
            contacts = self.get_results(api_call, etag, etag_function)
            self.__remove(enum_owner, service_module)
            for c in contacts:
                self.process_contact(c, enum_owner, service_module)
            if enum_owner == contact_owner.pilot and self.character_id is not None:
                self.object_contacts_pilots.append(
                    tb_contacts_pilots(self.character_id, enum_owner, 10.0, service_module))
            elif enum_owner == contact_owner.corp and self.corporation_id is not None:
                self.object_contacts_corps.append(
                    tb_contacts_corps(self.corporation_id, enum_owner, 10.0, service_module))
            elif enum_owner == contact_owner.alliance and self.alliance_id is not None:
                self.object_contacts_alliances.append(
                    tb_contacts_alliances(self.alliance_id, enum_owner, 10.0, service_module))
            else:
                pass
            self.last_updated = datetime.datetime.utcnow()
            self.last_modified = datetime.datetime.utcnow()
        except ApiException as ex:
            if ex.status == 304:  # nochanges
                self.last_updated = datetime.datetime.utcnow()
            if ex.status == 403:  # changed alliance/corp
                self.corporation_id = None
                self.alliance_id = None
                self.__remove(enum_owner, service_module)
        except Exception as ex:
            print(ex)

    def update_contacts(self, service_):
        if self.token is not None:
            self.write_changes(self.__alliance_api_call, self.etag_alliance, self.__set_alliance_etag,
                               contact_owner.alliance,
                               service_) if self.alliance_id else None
            self.write_changes(self.__corp_api_call, self.etag_corp, self.__set_corp_etag, contact_owner.corp,
                               service_) if self.corporation_id else None
            self.write_changes(self.__pilot_api_call, self.etag_character, self.__set_pilot_etag, contact_owner.pilot,
                               service_) if self.character_id else None

    @classmethod
    def generate_from_auth(cls, discord_user_id, auth_code, service_module):
        db: Session = service_module.get_session()
        try:
            clean_auth = service_module.sso.clean_auth_code(auth_code)
        except KeyError:
            raise InsightExc.SSO.SSOerror("You entered an invalid URL. Please try again.")
        try:
            response = service_module.sso.get_token_from_auth(clean_auth)
        except:
            raise InsightExc.SSO.SSOerror(
                "An error occurred when attempting to get a token from the auth code. Please try again later.")
        try:
            __row = cls(discord_user_id, response.get("refresh_token"))
            __row.get_affiliation(response.get("access_token"), service_module)
            db.merge(__row)
            db.commit()
            name_resolver.api_mass_name_resolve(service_module)
            return db.query(cls).filter(cls.discord_user == discord_user_id,
                                        cls.refresh_token == response.get("refresh_token")).one()
        except Exception as ex:
            print(ex)
            raise InsightExc.Db.DatabaseError
        finally:
            db.close()

    @classmethod
    def sync_all_tokens(cls, discord_user_id, service_module):
        db: Session = service_module.get_session()
        try:
            tokens = db.query(cls).filter(cls.discord_user == discord_user_id).all()
            for t in tokens:
                service_module.sso.get_token(t)
            db.commit()
            tokens = db.query(cls).filter(cls.discord_user == discord_user_id, cls.token.isnot(None)).all()
            for t in tokens:
                t.update_contacts(service_module)
            db.commit()
        except Exception as ex:
            print(ex)
        finally:
            db.close()

    @classmethod
    def mass_sync_all(cls, service_module):
        db: Session = service_module.get_session()
        try:
            ids = [id.discord_user for id in db.query(cls.discord_user).distinct()]
            db.close()
            for id in ids:
                cls.sync_all_tokens(id, service_module)
        except Exception as ex:
            print(ex)
        finally:
            db.close()


from ..filters import *
from ..eve import *
from . import *
import service
