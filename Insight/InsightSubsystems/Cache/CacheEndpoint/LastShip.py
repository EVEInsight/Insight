from InsightSubsystems.Cache.CacheEndpoint.AbstractMultiEndpoint import AbstractMultiEndpoint
from database.db_tables import tb_kills, tb_victims, tb_attackers, tb_types, tb_groups, tb_categories, \
    tb_characters, tb_corporations, tb_alliances, tb_systems, tb_locations, tb_temp_intjoin
from sqlalchemy.orm import Session, selectinload
from datetime import datetime
from sqlalchemy import func
import asyncio


class LastShip(AbstractMultiEndpoint):
    def __init__(self, cache_manager):
        self.wl_categories = [
            6, # ships
            65 # structures
        ]
        self.group_id_pod = 29
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
        self.precache: int = self.config.get("SUBSYSTEM_CACHE_LASTSHIP_PRECACHE_SECONDS")
        self.lock_char_ids_recent_activity = asyncio.Lock(loop=self.loop)
        self.char_ids_recent_activity = set()
        self.ttl = self.config.get("SUBSYSTEM_CACHE_LASTSHIP_TTL")

    @staticmethod
    def default_ttl() -> int:
        return 7200  # 2 hours

    @staticmethod
    def _get_unprefixed_key_hash_sync(query_item: int, **kwargs):
        return "{}".format(query_item)

    async def get(self, char_ids: list, **kwargs) -> dict:
        return await super().get(query_list=char_ids, **kwargs)

    async def delete_no_fail(self, char_id: int):
        return await super().delete_no_fail(query_item=char_id)

    def query_victim(self, db: Session, random_key, epoch):
        all_km_ids_pilots = db.query(
            tb_victims.character_id, tb_victims.kill_id
        ).select_from(tb_temp_intjoin). \
            join(tb_victims, tb_temp_intjoin.int_field == tb_victims.character_id, isouter=False). \
            join(tb_types, tb_victims.ship_type_id == tb_types.type_id, isouter=False). \
            join(tb_groups, tb_types.group_id == tb_groups.group_id, isouter=False). \
            filter(tb_groups.category_id.in_(self.wl_categories)). \
            filter(tb_temp_intjoin.key == random_key, tb_temp_intjoin.epoch == epoch).subquery()

        all_kms_with_row_nums = db.query(
            all_km_ids_pilots.c.character_id,
            all_km_ids_pilots.c.kill_id,
            (func.ROW_NUMBER().over(partition_by=all_km_ids_pilots.c.character_id,
                                    order_by=tb_kills.killmail_time.desc())).label("time_rank")
        ).select_from(all_km_ids_pilots). \
            join(tb_kills, tb_kills.kill_id == all_km_ids_pilots.c.kill_id, isouter=False).subquery()

        most_recent_pk = db.query(all_kms_with_row_nums.c.character_id, all_kms_with_row_nums.c.kill_id). \
            select_from(all_kms_with_row_nums). \
            filter(all_kms_with_row_nums.c.time_rank == 1).subquery()

        queried_chars_to_victims = db.query(most_recent_pk.c.character_id, tb_victims). \
            select_from(most_recent_pk). \
            join(tb_victims, tb_victims.kill_id == most_recent_pk.c.kill_id, isouter=False).\
            options(selectinload("object_kill").selectinload("object_victim"))

        return queried_chars_to_victims

    def query_attacker(self, db: Session, random_key, epoch):
        all_km_ids_pilots = db.query(
            tb_attackers.character_id, tb_attackers.no_pk, tb_attackers.kill_id
        ).select_from(tb_temp_intjoin).\
            join(tb_attackers, tb_temp_intjoin.int_field == tb_attackers.character_id, isouter=False).\
            join(tb_types, tb_attackers.ship_type_id == tb_types.type_id, isouter=False).\
            join(tb_groups, tb_types.group_id == tb_groups.group_id, isouter=False). \
            filter(tb_groups.category_id.in_(self.wl_categories)).\
            filter(tb_temp_intjoin.key == random_key, tb_temp_intjoin.epoch == epoch).subquery()

        all_kms_with_row_nums = db.query(
            all_km_ids_pilots.c.character_id,
            all_km_ids_pilots.c.no_pk,
            (func.ROW_NUMBER().over(partition_by=all_km_ids_pilots.c.character_id, order_by=tb_kills.killmail_time.desc())).label(
                "time_rank")
        ).select_from(all_km_ids_pilots).\
            join(tb_kills, tb_kills.kill_id == all_km_ids_pilots.c.kill_id, isouter=False).subquery()

        most_recent_pk = db.query(all_kms_with_row_nums.c.character_id, all_kms_with_row_nums.c.no_pk).\
            select_from(all_kms_with_row_nums).\
            filter(all_kms_with_row_nums.c.time_rank == 1).subquery()

        queried_chars_to_attackers = db.query(most_recent_pk.c.character_id, tb_attackers).\
            select_from(most_recent_pk).\
            join(tb_attackers, tb_attackers.no_pk == most_recent_pk.c.no_pk, isouter=False). \
            options(selectinload("object_kill").selectinload("object_attackers"))

        return queried_chars_to_attackers

    def _last_ships(self, db: Session, random_key, epoch, attacker=True):
        if attacker:
            query = self.query_attacker(db, random_key, epoch)
        else:
            query = self.query_victim(db, random_key, epoch)
        return_dict = {}
        for t in query.all():
            return_dict[t[0]] = t[1]
        return return_dict

    def get_group_id(self, db_row):
        if isinstance(db_row, tb_attackers) or isinstance(db_row, tb_victims):
            if isinstance(db_row.object_ship, tb_types):
                if isinstance(db_row.object_ship.object_group, tb_groups):
                    return db_row.object_ship.object_group.group_id
        return -1

    def get_last_ship(self, last_a, last_v):
        if isinstance(last_a, tb_attackers) and not isinstance(last_v, tb_victims):
            return (last_a, True)
        elif not isinstance(last_a, tb_attackers) and isinstance(last_v, tb_victims):
            return (last_v, False)
        elif not isinstance(last_a, tb_attackers) and not isinstance(last_v, tb_victims):
            return (None, True)
        else:
            return_item = (last_a, True)
            v_item: tb_victims = last_v
            v_group: int = self.get_group_id(v_item)
            a_item: tb_attackers = return_item[0]
            a_group = self.get_group_id(a_item)
            a_time: datetime = a_item.object_kill.killmail_time
            v_time: datetime = v_item.object_kill.killmail_time
            if a_time and v_time:
                if v_time >= a_time:
                    if v_group == self.group_id_pod and (v_time - a_time).total_seconds() <= 900:
                        return_item = (a_item, False)
                    else:
                        return_item = (v_item, False)
                else:
                    if a_group == self.group_id_pod and (a_time - v_time).total_seconds() <= 900:
                        return_item = (v_item, False)
                    else:
                        return_item = (a_item, True)
            elif v_time:
                return_item = (v_item, False)
            else:
                pass
        return return_item

    def _make_dict(self, char_id, involved_row, is_alive) -> dict:
        d = {
            "data": {
                "known": False,
                "queryID": char_id
            }
        }
        if char_id and isinstance(char_id, int):
            if isinstance(involved_row, tb_attackers) or isinstance(involved_row, tb_victims):
                d["data"]["known"] = True
                d["data"]["attacker"] = is_alive
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
                    if isinstance(km.object_location, tb_locations):
                        d["data"]["location"] = km.object_location.to_jsonDictionary()
                    d["data"]["km"] = km.to_jsonDictionary()
        return d

    def _do_endpoint_logic_sync(self, lookup_dict: dict, **kwargs) -> dict:
        character_ids = set()
        return_dict = {}
        for char_id in lookup_dict.keys():
            character_ids.add(char_id)
            return_dict[char_id] = None
        db = self.db_sessions.get_session()
        try:
            random_key = tb_temp_intjoin.get_random_key()
            epoch = tb_temp_intjoin.get_epoch()
            for c in character_ids:
                db.add(tb_temp_intjoin(random_key, epoch, c))
            db.commit()
            attackers = self._last_ships(db, random_key, epoch, attacker=True)
            victims = self._last_ships(db, random_key, epoch, attacker=False)
            db.expunge_all()
            for c_id in character_ids:
                last_ship, is_alive = self.get_last_ship(attackers.get(c_id), victims.get(c_id))
                return_dict[c_id] = self._make_dict(c_id, last_ship, is_alive)
        finally:
            db.close()
        return return_dict

    def reset_last_ships_background(self, new_km: tb_kills):
        self.loop.create_task(self._reset_last_ship(new_km))

    async def _reset_last_ship(self, new_km: tb_kills):
        pilot_ids = await self.executor(self._extract_characters, new_km)
        for pilot_id in pilot_ids:
            delete_attempts = 0
            while True:
                if await self.delete_no_fail(char_id=pilot_id):
                    break
                else:
                    if delete_attempts >= 10:
                        print("Unable to delete the last ship for pilot id: {} from the cache. Is Redis connected?".format(pilot_id))
                        break
                    else:
                        await asyncio.sleep(max(1, delete_attempts * 10))
                        delete_attempts += 1
            async with self.lock_char_ids_recent_activity:
                self.char_ids_recent_activity.add(pilot_id)

    def _extract_characters(self, new_km: tb_kills):
        char_ids = []
        if new_km.object_attackers:
            for a in new_km.object_attackers:
                char_id = a.character_id
                if char_id:
                    char_ids.append(char_id)
        if new_km.object_victim and new_km.object_victim.character_id:
            char_ids.append(new_km.object_victim.character_id)
        return char_ids

    async def cron_precache_operation(self):
        async with self.lock_char_ids_recent_activity:
            if self.precache <= 0: # disabled
                self.char_ids_recent_activity = set()
                return
            if len(self.char_ids_recent_activity) > 0:
                old_set = self.char_ids_recent_activity
                self.char_ids_recent_activity = set()
                await self.get(char_ids=old_set)  # safe for set does not have to be list

    def ttl_override(self) -> int:
        return self.ttl
