from .base_objects import *
from . import categories,types
from .sde_importer import *


class Groups(dec_Base.Base,individual_api_pulling,index_api_updating,sde_impoter):
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True, index=True)
    category_id = Column(Integer,ForeignKey("categories.category_id"),nullable=True)
    published = Column(Boolean,default=True)
    api_ETag = Column(String, default=None, nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_types = relationship("Types",uselist=True,back_populates="object_group")
    object_category = relationship("Categories",uselist=False,back_populates="object_groups",lazy="joined")

    def __init__(self, eve_id: int):
        self.group_id = eve_id
        self._types = None

    def load_fk_objects(self):
        if self.category_id:
            self.object_category = categories.Categories(self.category_id)
        if self._types:
            self.object_types = []
            for object_id in self._types:
                self.object_types.append(types.Types(object_id))

    def get_id(self):
        return self.group_id

    def get_name(self):
        return self.name

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_groups_with_http_info(**kwargs)

    def get_response(self, api, **kwargs):
        return api.get_universe_groups_group_id_with_http_info(group_id=self.group_id, **kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.category_id = response.get("category_id")
        self.published = response.get("published")
        self._types = response.get("types")

    @classmethod
    def primary_key_row(cls):
        return cls.group_id

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.groupID)
        new_row.name = __row.groupName
        new_row.category_id = __row.categoryID
        new_row.published = __row.published
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.name is None or self.category_id is None

    @need_api.expression
    def need_api(cls):
        return or_(cls.name.is_(None),cls.category_id.is_(None))

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.group_id for i in
                        service_module.get_session().query(cls.group_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.groupID for i in sde_session.query(sde_base.groupID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.groupID

    def to_jsonDictionary(self) -> dict:
        return {
            "group_id": self.group_id,
            "group_name": self.name,
            "published": self.published,
            "category": self.object_category.to_jsonDictionary() if self.object_category else None
        }
