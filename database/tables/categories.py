from database.tables.base_objects import *


class Categories(Base,individual_api_pulling,index_api_updating):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    published = Column(Boolean,default=True)
    api_ETag = Column(String, default=None, nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_groups = relationship("Groups",uselist=True,back_populates="object_category")

    def __init__(self, eve_id: int):
        self.category_id = eve_id

    def load_fk_objects(self):
        if self.__groups:
            self.object_groups = []
            for object_id in self.__groups:
                self.object_groups.append(database.tables.groups.Groups(object_id))

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