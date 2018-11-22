import re
import traceback
import InsightLogger


class InsightAdmins(object):
    def __init__(self):
        self.logger = InsightLogger.InsightLogger.get_logger('AdminModule', 'AdminModule.log')
        self.__admins = set()
        self.top_admin = None
        self.__file_name = "InsightAdmins.txt"
        self.__read_admins()
        self.print_admins()

    def __read_admins(self):
        try:
            with open(self.__file_name, 'r') as f:
                reg = re.compile('#.*?#', re.DOTALL)
                text = re.sub(reg, '', f.read())
                for i in text.split():
                    try:
                        self.__admins.add(int(i))
                        if self.top_admin is None:
                            self.top_admin = int(i)
                    except ValueError:
                        print("'{}' - is not a valid Discord user id in the '{}' file.".format(i, self.__file_name))
        except FileNotFoundError:
            with open(self.__file_name, 'w') as f:
                comment = "# This is a list of Discord user IDs that can access Insight admin functionality. " \
                          "(!quit, etc commands). To make a user an admin, copy their user ID from Discord and add " \
                          "it to this file, restarting the bot if it's running. Multiple admins can exist, but be " \
                          "sure to separate IDs with spaces or newlines. #\n\n"
                f.write(comment)
                print("Created a new '{}' file. Add Discord user ids to this file to allow certain users to access"
                      " Insight administrator functionality commands.".format(self.__file_name))

    def print_admins(self):
        if len(self.__admins) > 0:
            div = '======================='
            print(div)
            print('Insight Admin Discord User IDs:')
            for i in self.__admins:
                print(i)
            print(div)

    def is_admin(self, other_id):
        try:
            is_admin = int(other_id) in self.__admins
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


