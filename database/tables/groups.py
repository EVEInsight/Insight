from database.tables.base_objects import *


class Groups(Base,individual_api_pulling,index_api_updating):
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True, nullable=False,autoincrement=False)
    name = Column(String,default=None,nullable=True,index=True)
    category_id = Column(Integer,ForeignKey("categories.category_id"),nullable=True)
    published = Column(Boolean,default=True)
    api_ETag = Column(String, default=None, nullable=True)
    api_Expires = Column(DateTime,default=None,nullable=True)
    api_Last_Modified = Column(DateTime,default=None,nullable=True)

    object_types = relationship("Types",uselist=True,back_populates="object_group")
    object_category = relationship("Categories",uselist=False,back_populates="object_groups")

    def __init__(self, eve_id: int):
        self.group_id = eve_id

    def load_fk_objects(self):
        if self.category_id:
            self.object_category = database.tables.categories.Categories(self.category_id)
        if self.__types:
            self.object_types = []
            for object_id in self.__types:
                self.object_types.append(database.tables.types.Types(object_id))

    def get_id(self):
        return self.group_id

    @classmethod
    def index_swagger_api_call(cls, api, **kwargs):
        return api.get_universe_groups_with_http_info(**kwargs)

    def get_response(self, api, **kwargs):
        return api.get_universe_groups_group_id_with_http_info(group_id=self.group_id, **kwargs)

    def process_body(self,response):
        self.name = response.get("name")
        self.category_id = response.get("category_id")
        self.published = response.get("published")
        self.__types = response.get("types")

    @classmethod
    def primary_key_row(cls):
        return cls.group_id