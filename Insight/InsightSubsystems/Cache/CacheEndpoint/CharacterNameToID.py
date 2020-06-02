from InsightSubsystems.Cache.CacheEndpoint.AbstractMultiEndpoint import AbstractMultiEndpoint
from database.db_tables import tb_characters, tb_temp_strjoin
from InsightUtilities.StaticHelpers import RegexCheck
import InsightExc
from sqlalchemy.orm import Session, noload


class CharacterNameToID(AbstractMultiEndpoint):
    @staticmethod
    def default_ttl() -> int:
        return 172800  # 2 days

    @staticmethod
    def _get_unprefixed_key_hash_sync(query_item: str, **kwargs):
        return "{}".format(query_item)

    async def get(self, char_names: list, **kwargs) -> dict:
        return await super().get(query_list=char_names, **kwargs)

    def query_attacker(self, db: Session, random_key, epoch):
        q = db.query(tb_temp_strjoin.str_field, tb_characters).\
            select_from(tb_temp_strjoin).\
            join(tb_characters, tb_temp_strjoin.str_field == tb_characters.character_name, isouter=False). \
            filter(tb_temp_strjoin.key == random_key, tb_temp_strjoin.epoch == epoch). \
            options(noload("*"))
        return q

    def _make_dict(self, query_name: str, row_character_name: tb_characters):
        d = {
            "data": {}
        }
        if isinstance(row_character_name, tb_characters):
            d["data"] = {
                "name": row_character_name.character_name,
                "id": row_character_name.character_id,
                "found": True
            }
            self.set_min_ttl(d, self.default_ttl())
        else:
            d["data"] = {
                "name": query_name,
                "id": None,
                "found": False
            }
            self.set_min_ttl(d, 10800)  # 3 hours
        return d

    def _do_endpoint_logic_sync(self, lookup_dict: dict, **kwargs) -> dict:
        character_names = set()
        return_dict = {}
        for char_name in lookup_dict.keys():
            if RegexCheck.is_valid_character_name(char_name):
                character_names.add(char_name)
                return_dict[char_name] = None
            else:
                raise InsightExc.userInput.InvalidInput("Invalid character name was submitted.")
        db = self.db_sessions.get_session()
        try:
            random_key = tb_temp_strjoin.get_random_key()
            epoch = tb_temp_strjoin.get_epoch()
            for c in character_names:
                db.add(tb_temp_strjoin(random_key, epoch, c))
            db.commit()
            for t in self.query_attacker(db, random_key=random_key, epoch=epoch).all():
                char_name = t[0]
                return_dict[char_name] = self._make_dict(char_name, t[1])
                character_names.remove(t[0])
            for char_name in character_names:
                return_dict[char_name] = self._make_dict(char_name, None)
        finally:
            db.close()
        return return_dict

