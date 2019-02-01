import re
import traceback
import InsightLogger


class InsightAdmins(object):
    def __init__(self):
        self.logger = InsightLogger.InsightLogger.get_logger('AdminModule', 'AdminModule.log')
        self._admins = set()
        self.top_admin = None
        self._file_name = "InsightAdmins.txt"
        self._read_admins()
        self.print_admins()

    def _read_admins(self):
        try:
            with open(self._file_name, 'r') as f:
                reg = re.compile('#.*?#', re.DOTALL)
                text = re.sub(reg, '', f.read())
                for i in text.split():
                    try:
                        self._admins.add(int(i))
                        if self.top_admin is None:
                            self.top_admin = int(i)
                    except ValueError:
                        print("'{}' - is not a valid Discord user id in the '{}' file.".format(i, self._file_name))
        except FileNotFoundError:
            with open(self._file_name, 'w') as f:
                comment = "# This is a list of Discord user IDs that can access Insight admin functionality. " \
                          "(!quit, etc commands). To make a user an admin, copy their user ID from Discord and add " \
                          "it to this file, restarting the bot if it's running. Multiple admins can exist, but be " \
                          "sure to separate IDs with spaces or newlines. #\n\n"
                f.write(comment)
                print("Created a new '{}' file. Add Discord user ids to this file to allow certain users to access"
                      " Insight administrator functionality commands.".format(self._file_name))

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


