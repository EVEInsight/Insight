from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from database.db_tables import tb_characters


class CharacterNameToID(AbstractEndpoint):
    def default_ttl(self) -> int:
        return 3600

    def _get_unprefixed_key_hash_sync(self, char_name: str):
        return "{}".format(char_name)

    async def get(self, char_name: str) -> dict:
        return await super().get(char_name=char_name)

    def _do_endpoint_logic_sync(self, char_name: str) -> dict:
        db = self.db_sessions.get_session()
        d = {
            "data": {}
        }
        try:
            c = db.query(tb_characters).filter(tb_characters.character_name == char_name).one_or_none()
            if isinstance(c, tb_characters):
                d["data"] = {
                    "name": c.character_name,
                    "id": c.character_id,
                    "found": True
                }
                self.set_min_ttl(d, 172800)  # 2 days
            else:
                d["data"] = {
                    "name": char_name,
                    "id": None,
                    "found": False
                }
                self.set_min_ttl(d, 14400)  # 4 hours
        finally:
            db.close()
        return d
