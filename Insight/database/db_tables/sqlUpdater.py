from distutils.version import LooseVersion
import sys
import service


class sqlUpdater(object):
    def __init__(self, engine, current_version):
        self.connection = engine.connect()
        self.current_version = current_version
        self.updated_version = current_version

    def compatibility_check(self):
        if self.current_version > service.ServiceModule.get_version():
            print("You cannot downgrade to a version of Insight below {0} as there will be"
                  " database compatibility issues. Insight releases are forward compatible, but in this case"
                  " only backward compatible to version {0}. If you wish to downgrade to an older version"
                  " you must first delete your database file.".format(str(self.current_version)))
            sys.exit(1)

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
        yield ('ALTER TABLE discord_enFeed ADD template_id INTEGER DEFAULT 0 NOT NULL;')
        yield ('ALTER TABLE discord_capRadar ADD template_id INTEGER DEFAULT 0 NOT NULL;')

    def update_all(self):
        """Updates tables, returning the latest successful updated version"""
        self.compatibility_check()
        error = False
        for i in self.get_versions_higher():
            try:
                results = list(i())
                print('Updating database to version: {}'.format(i.__doc__))
                self.__execute_statements(results)
                self.updated_version = i.__doc__
            except Exception as ex:
                print(ex)
                error = True
                break
        return (str(self.updated_version), error)

