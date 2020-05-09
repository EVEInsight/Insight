from InsightSubsystems.Cache.CacheEndpoint.AbstractEndpoint import AbstractEndpoint
from database.db_tables import tb_kills, tb_victims, tb_attackers, tb_types, tb_groups, tb_categories, \
    tb_characters, tb_corporations, tb_alliances, tb_systems
from sqlalchemy.orm import Session
from datetime import datetime


class LastShip(AbstractEndpoint):
    def __init__(self, cache_manager):
        self.categories = [
            6, # ships
            65 # structures
        ]
        self.super_titans = [
            30, # titans
            659 # supercarriers
        ]
        self.regular_capitals = [
            547, # carrier
            485, #dreads
            1538, #fax
            883 # cap industrial
        ]
        super().__init__(cache_manager)

    @staticmethod
    def default_ttl() -> int:
        return 7200

    @staticmethod
    def _get_unprefixed_key_hash_sync(char_id: int):
        return "{}".format(char_id)

    async def get(self, char_id: int) -> dict:
        return await super().get(char_id=char_id)

    def _generator_last_ships(self, db: Session, character_id: int, attacker=True):
        mail_pos = 2e+9
        while True:
            if attacker:
                row_class = tb_attackers
            else:
                row_class = tb_victims
            q = db.query(row_class). \
                join(tb_kills, row_class.kill_id == tb_kills.kill_id). \
                join(tb_types, row_class.ship_type_id == tb_types.type_id). \
                join(tb_groups, tb_types.group_id == tb_groups.group_id). \
                join(tb_categories, tb_groups.category_id == tb_categories.category_id). \
                filter(row_class.character_id == character_id). \
                filter(tb_categories.category_id.in_(self.categories)). \
                filter(tb_kills.kill_id < mail_pos). \
                order_by(tb_kills.killmail_time.desc()).limit(2)
            rows = q.all()
            for row in rows:
                if row.kill_id < mail_pos:
                    mail_pos = mail_pos
                yield row
            if len(rows) == 0:
                break
        return

    def get_last_ship(self, db: Session, character_id: int):
        gen_kms_a = self._generator_last_ships(db, character_id, attacker=True)
        gen_kms_v = self._generator_last_ships(db, character_id, attacker=False)
        return_item = None
        try:
            return_item = next(gen_kms_a)
        except StopIteration:
            pass
        try:
            v_item: tb_victims = next(gen_kms_v)
            a_item: tb_attackers = return_item
            if isinstance(a_item, tb_attackers):
                a_time = a_item.object_kill.killmail_time
                v_time = v_item.object_kill.killmail_time
                if a_time and v_time:
                    if v_time >= a_time:
                        return_item = v_item
                elif v_time:
                    return_item = v_item
                else:
                    pass
        except StopIteration:
            pass
        return return_item

    def _do_endpoint_logic_sync(self, char_id: int) -> dict:
        db = self.db_sessions.get_session()
        d = {
            "data": {
                "known": False,
                "queryID": char_id
            }
        }
        try:
            if char_id and isinstance(char_id, int):
                involved_row = self.get_last_ship(db, char_id)
                if isinstance(involved_row, tb_attackers) or isinstance(involved_row, tb_victims):
                    d["data"]["known"] = True
                    if isinstance(involved_row, tb_attackers):
                        d["data"]["attacker"] = True
                    else:
                        d["data"]["attacker"] = False
                    if isinstance(involved_row.object_pilot, tb_characters):
                        d["data"]["character"] = involved_row.object_pilot.to_jsonDictionary()
                    if isinstance(involved_row.object_corp, tb_corporations):
                        d["data"]["corporation"] = involved_row.object_corp.to_jsonDictionary()
                    if isinstance(involved_row.object_alliance, tb_alliances):
                        d["data"]["alliance"] = involved_row.object_alliance.to_jsonDictionary()
                    if isinstance(involved_row.object_ship, tb_types):
                        d["data"]["ship"] = involved_row.object_ship.to_jsonDictionary()
                        if isinstance(involved_row.object_ship.object_group, tb_groups):
                            group_id = involved_row.object_ship.object_group.group_id
                            if group_id:
                                if group_id in self.super_titans:
                                    d["data"]["isSuperTitan"] = True
                                else:
                                    d["data"]["isSuperTitan"] = False
                                if group_id in self.regular_capitals:
                                    d["data"]["isRegularCap"] = True
                                else:
                                    d["data"]["isRegularCap"] = False
                    if isinstance(involved_row, tb_attackers):
                        if isinstance(involved_row.object_weapon, tb_types):
                            d["data"]["weapon"] = involved_row.object_weapon.to_jsonDictionary()
                    km = involved_row.object_kill
                    if isinstance(km, tb_kills):
                        if isinstance(km.object_system, tb_systems):
                            d["data"]["system"] = km.object_system.to_jsonDictionary()
                        if isinstance(km.killmail_time, datetime):
                            d["data"]["time"] = str(km.killmail_time)
                        else:
                            d["data"]["time"] = str(datetime(year=2008, month=5, day=6))
                        d["data"]["km"] = km.to_jsonDictionary()
        finally:
            db.close()
        return d
