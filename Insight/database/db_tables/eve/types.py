from .base_objects import *
from .sde_importer import *
from . import groups


class Types(dec_Base.Base,name_only,index_api_updating,sde_impoter):
    __tablename__ = 'types'

    type_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    type_name = Column(String,default=None,nullable=True, index=True)
    description = Column(String,default="")
    basePrice = Column(DECIMAL(19,4),default=None,nullable=True)
    group_id = Column(Integer,ForeignKey("groups.group_id"),nullable=True, index=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_group = relationship("Groups",uselist=False,back_populates="object_types",lazy="joined")
    object_attacker_ships = relationship("Attackers", uselist=True,foreign_keys="Attackers.ship_type_id",back_populates="object_ship")
    object_attacker_weapons = relationship("Attackers", uselist=True,foreign_keys="Attackers.weapon_type_id",back_populates="object_weapon")
    object_loses_ships = relationship("Victims", uselist=True, back_populates="object_ship")

    def __init__(self, type_id: int):
        self.type_id = type_id

    def load_fk_objects(self):
        if self.group_id:
            self.object_group = groups.Groups(self.group_id)

    def session_add_nonexists_fk(self, db: Session):
        if self.group_id and not groups.Groups.session_exists(self.group_id, db):
            db.add(groups.Groups(self.group_id))

    def get_id(self):
        return self.type_id

    def get_name(self):
        return self.type_name

    def set_name(self, api_name):
        self.type_name = api_name

    def get_category(self):
        try:
            return self.object_group.object_category.category_id
        except:  # no category or object error
            return None

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_types_with_http_info(**kwargs)

    @hybrid_property
    def need_name(self):
        return self.type_name == None

    @classmethod
    def primary_key_row(cls):
        return cls.type_id

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.typeID)
        new_row.type_name = __row.typeName
        new_row.group_id = __row.groupID
        new_row.description = __row.description
        new_row.basePrice = __row.basePrice
        return new_row

    @hybrid_property
    def need_api(self):
        return self.type_name is None or self.group_id is None

    @need_api.expression
    def need_api(cls):
        return or_(cls.type_name.is_(None), cls.group_id.is_(None))

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.type_id for i in
                        service_module.get_session().query(cls.type_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.typeID for i in sde_session.query(sde_base.typeID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.typeID

    @classmethod
    def auto_adjust_helper(cls, current_price, if_less_than_this, set_to_this):
        if current_price is None or current_price <= if_less_than_this:
            return set_to_this
        else:
            return current_price

    @classmethod
    def update_prices(cls, service_module):
        db: Session = service_module.get_session()
        try:
            total_market = 0
            resp: List[swagger_client.GetMarketsPrices200Ok] = swagger_client.MarketApi().get_markets_prices()
            item_dict = {}
            for i in resp:
                item_dict[i.type_id] = i
            for t in db.query(cls).all():
                p = item_dict.get(t.get_id())
                if p is not None:
                    if p.average_price is not None:
                        price = p.average_price
                    elif p.adjusted_price is not None:
                        price = p.adjusted_price
                    else:
                        price = t.basePrice
                    t.basePrice = price
                    total_market += 1
                try:
                    if t.group_id == 30:  # faction titan price auto adjust
                        t.basePrice = cls.auto_adjust_helper(t.basePrice, 30e9, 300e9)
                    elif t.group_id == 659:  # super
                        t.basePrice = cls.auto_adjust_helper(t.basePrice, 8e9, 95e9)
                    elif t.group_id == 1538:  # fax
                        t.basePrice = cls.auto_adjust_helper(t.basePrice, .7e9, 10e9)
                    elif t.group_id == 485:  # dread
                        t.basePrice = cls.auto_adjust_helper(t.basePrice, .7e9, 15e9)
                    elif t.group_id == 547:  # carrier
                        t.basePrice = cls.auto_adjust_helper(t.basePrice, .7e9, 13e9)
                    else:
                        pass
                except Exception as ex:
                    print(ex)
            db.commit()
            print("Updated prices for {} items.".format(str(total_market)))
        except ApiException as ex:
            print("Error code {} when updating market data.".format(str(ex.status)))
        except Exception as ex:
            print(ex)

    def to_jsonDictionary(self) -> dict:
        d = {}
        category_id = self.get_category()
        if isinstance(category_id, int) and category_id == 6:
            group_id = self.group_id
            if isinstance(group_id, int):
                if group_id in [30, 659]:
                    d["isSuperTitan"] = True
                    d["isCap"] = True
                else:
                    d["isSuperTitan"] = False
                if group_id in [547, 485, 1538, 883]:
                    d["isCap"] = True
                else:
                    d["isCap"] = False
        d["type_id"] = self.type_id
        d["type_name"] = self.type_name
        d["basePrice"] = float(self.basePrice) if self.basePrice else None
        d["group"] = self.object_group.to_jsonDictionary() if self.object_group else None
        return d
