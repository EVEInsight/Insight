from distutils.version import LooseVersion
import sys
import service


class sqlUpdater(object):
    def __init__(self, engine, current_version):
        self.connection = engine.connect()
        self.current_version = current_version
        self.updated_version = current_version

    def compatibility_check(self):
        if self.current_version > service.ServiceModule.get_db_version():
            print("You cannot downgrade to a version of Insight with a database version below {0} as there will be"
                  " database compatibility issues. Insight releases are forward compatible, but in this case"
                  " only backward compatible to a release with database version {0}. If you wish to downgrade to an "
                  "older version that uses a database version below {0} you must first delete your database file."
                  .format(str(self.current_version)))
            sys.exit(1)

    def get_approval(self, changes):
        print("Insight Database Updater Warning: Certain updates modify the architecture of the database file that "
              "require your approval. \nThis new update will make the following changes:\n\n")
        print(changes + '\n')
        resp = input("\nProceed with these changes? Note: You will be unable to use this version of Insight unless you "
                     "approve.[Y/N]: ").lower()
        if resp.startswith('y'):
            return
        elif resp.startswith('n'):
            print("No changes you were made. If you wish to continue using your database without changes then you must "
                  "downgrade to an older, unsupported Insight release.")
            sys.exit(1)
        else:
            print("Unknown response. No changes were made.")
            sys.exit(1)

    def get_versions_higher(self):
        for i in dir(self):
            if i.startswith("sqlV"):
                func = getattr(self, i)
                if LooseVersion(func.__doc__) > self.current_version:
                    yield func

    def __execute_statements(self, statements):
        for i in statements:
            print('Executing statement: {}'.format(str(i)))
            self.connection.execute(i)

    def sqlV_0_12_1(self):
        """v0.12.1"""
        for i in self.sqlV_0_12_0():
            yield i

    def sqlV_0_12_0(self):
        """v0.12.0"""
        changes = "- Delete all access tokens.\n- Require users to readd their standing tokens.\n+ Encrypt all " \
                  "new access tokens using a generated secret key."
        self.get_approval(changes)
        yield 'DROP TABLE IF EXISTS contacts_alliances;'
        yield 'DROP TABLE IF EXISTS contacts_corporations;'
        yield 'DROP TABLE IF EXISTS contacts_characters;'
        yield 'DROP TABLE IF EXISTS discord_tokens;'
        yield 'DROP TABLE IF EXISTS tokens;'

    def sqlV_1_1_0(self):
        """v1.1.0"""
        yield 'ALTER TABLE discord_channels ADD appearance_id INTEGER DEFAULT 0 NOT NULL;'

    def sqlV_0_10_1(self):
        """v0.10.1"""
        yield 'ALTER TABLE discord_enFeed ADD template_id INTEGER DEFAULT 0 NOT NULL;'
        yield 'ALTER TABLE discord_capRadar ADD template_id INTEGER DEFAULT 0 NOT NULL;'

    def sqlV_1_2_0(self):
        """v1.2.0"""
        yield 'ALTER TABLE discord_enFeed ADD minValue FLOAT DEFAULT 0.0 NOT NULL;'

    def sqlV_1_3_0(self):
        """v1.3.0"""
        yield 'CREATE INDEX ix_attackers_kill_id on attackers (kill_id);'

    def sqlV_2_1_0(self):
        """v2.1.0"""
        yield 'CREATE INDEX ix_regions_name on regions (name);'
        yield 'CREATE INDEX ix_constellations_name on constellations (name);'
        yield 'CREATE INDEX ix_categories_name on categories (name);'
        yield 'CREATE INDEX ix_groups_name on groups (name);'
        yield 'CREATE INDEX ix_types_type_name on types (type_name);'

    def sqlV_2_2_0(self):
        """v2.2.0"""
        yield "alter table discord_channels add mention VARCHAR(9) DEFAULT 'noMention' not null;"
        yield 'alter table discord_channels add mention_every FLOAT DEFAULT 15.0 not null;'

    def sqlV_2_3_0(self):
        """v2.3.0"""
        yield "alter table discord_channels add modification_lock BOOLEAN DEFAULT 0 not null;"

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
                print('DB patch ok')
            except Exception as ex:
                print(ex)
                error = True
                break
        return (str(self.updated_version), error)

