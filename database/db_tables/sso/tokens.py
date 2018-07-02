from .sso_base import *
from ..eve import tb_alliances
import requests
import json
from requests.auth import HTTPBasicAuth
import swagger_client


class Tokens(dec_Base.Base, sso_base):
    __tablename__ = 'tokens'

    discord_user = Column(BIGINT, ForeignKey("discord_users.user_id"), primary_key=True, autoincrement=False,
                          nullable=False)
    refresh_token = Column(String, primary_key=True, nullable=False)
    character_id = Column(Integer, ForeignKey("characters.character_id"), nullable=True)
    corporation_id = Column(Integer, ForeignKey("corporations.corporation_id"), nullable=True)
    alliance_id = Column(Integer, ForeignKey("alliances.alliance_id"), nullable=True)
    last_updated = Column(DateTime)
    etag_character = Column(String, nullable=True)
    etag_corp = Column(String, nullable=True)
    etag_alliance = Column(String, nullable=True)

    object_user = relationship("Users", uselist=False, back_populates="object_tokens", lazy="joined")
    object_pilot = relationship("Characters", uselist=False, lazy="joined")
    object_corp = relationship("Corporations", uselist=False, lazy="joined")
    object_alliance = relationship("Alliances", uselist=False, lazy="joined")

    def __init__(self, discord_user, refresh_token):
        self.discord_user = discord_user
        self.refresh_token = refresh_token

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
            raise None

    @classmethod
    def generate_from_auth(cls, discord_user_id, auth_code, service_module):
        db: Session = service_module.get_session()
        try:
            clean_auth = service_module.sso.clean_auth_code(auth_code)
        except KeyError:
            return "You entered an invalid code. Please try again."
        try:
            response = service_module.sso.get_token_from_auth(clean_auth)
        except:
            return "An error occurred when attempting to get a token from the auth code. Please try again later."
        try:
            db.query(cls).filter(cls.discord_user == discord_user_id,
                                 cls.refresh_token == response.get("refresh_token")).one()
            db.close()
            return "This token already exists."
        except NoResultFound:
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
                return "An error occurred when attempting to get affiliation, please try again later!"
            finally:
                db.close()


from ..filters import *
from ..eve import *
import service
