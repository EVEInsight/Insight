from distutils.version import LooseVersion


class sqlUpdater(object):
    def __init__(self, engine, current_version):
        self.connection = engine.connect()
        self.current_version = current_version
        self.updated_version = current_version

    def get_versions_higher(self):
        for i in dir(self):
            if i.startswith("sqlV"):
                func = getattr(self, i)
                if LooseVersion(func.__doc__) > self.current_version:
                    yield func

    def __execute_statements(self, statements):
        for i in statements:
            self.connection.execute(i)

    def sqlV_0_10_1(self):
        """v0.10.1"""
        qs = []
        qs.append('ALTER TABLE discord_enFeed ADD template_id INTEGER DEFAULT 0 NOT NULL;')
        qs.append('ALTER TABLE discord_capRadar ADD template_id INTEGER DEFAULT 0 NOT NULL;')
        return qs

    def update_all(self):
        """Updates tables, returning the latest successful updated version"""
        error = False
        for i in self.get_versions_higher():
            try:
                results = i()
                self.__execute_statements(results)
                self.updated_version = i.__doc__
            except Exception as ex:
                print(ex)
                error = True
                break
        return (str(self.updated_version), error)
