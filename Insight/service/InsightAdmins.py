import traceback
import InsightLogger
import InsightUtilities


class InsightAdmins(object):
    def __init__(self):
        self.config = InsightUtilities.ConfigLoader()
        self.logger = InsightLogger.InsightLogger.get_logger('AdminModule', 'AdminModule.log')
        self._admins = set()
        self.top_admin = None
        self._read_admins()
        self.print_admins()

    def _read_admins(self):
        admins_parsed: list = self.config.get("INSIGHT_ADMINS")
        for i in admins_parsed:
            try:
                self._admins.add(int(i))
                if self.top_admin is None:
                    self.top_admin = int(i)
            except ValueError:
                print("'{}' - is not a valid Discord user id.".format(i))

    def print_admins(self):
        if len(self._admins) > 0:
            div = '======================='
            print(div)
            print('Insight Admin Discord User IDs:')
            for i in self._admins:
                print(i)
            print(div)

    def is_admin(self, other_id):
        try:
            is_admin = int(other_id) in self._admins
            if is_admin:
                self.logger.info("User '{}' is an admin.".format(other_id))
            else:
                self.logger.warning("User '{}' attempted to access an admin command and was denied.".format(other_id))
            return is_admin
        except Exception as ex:
            print("InsightAdmins error: {}".format(ex))
            traceback.print_exc()
            return False

    def get_default_admin(self):
        return self.top_admin


