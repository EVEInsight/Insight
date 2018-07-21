from .base_objects import *
from . import groups
from .sde_importer import *


class Categories(dec_Base.Base,individual_api_pulling,index_api_updating,sde_impoter):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True)
    published = Column(Boolean,default=True)
    api_ETag = Column(String, default=None, nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_groups = relationship("Groups",uselist=True,back_populates="object_category")

    def __init__(self, eve_id: int):
        self.category_id = eve_id
        self.__groups = None

    def load_fk_objects(self):
        if self.__groups:
            self.object_groups = []
            for object_id in self.__groups:
                self.object_groups.append(groups.Groups(object_id))

    def get_id(self):
        return self.category_id

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_categories_with_http_info(**kwargs)

    def get_response(self, api, **kwargs):
        return api.get_universe_categories_category_id_with_http_info(category_id=self.category_id,**kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.published = response.get("published")
        self.__groups = response.get("groups")

    @classmethod
    def primary_key_row(cls):
        return cls.category_id

    @classmethod
    def make_from_sde(cls,__row):
        new_row = cls(__row.categoryID)
        new_row.name = __row.categoryName
        new_row.published = __row.published
        new_row.load_fk_objects()
        return new_row

    @hybrid_property
    def need_api(self):
        return self.name is None

    @need_api.expression
    def need_api(cls):
        return cls.name.is_(None)

    @classmethod
    def get_missing_ids(cls, service_module, sde_session, sde_base):
        existing_ids = [i.category_id for i in
                        service_module.get_session().query(cls.category_id).filter(not_(cls.need_api)).all()]
        importing_ids = [i.categoryID for i in sde_session.query(sde_base.categoryID).all()]
        return list(set(importing_ids) - set(existing_ids))

    @classmethod
    def get_query_filter(cls, sde_base):
        return sde_base.categoryID