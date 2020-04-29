from InsightSubsystems import SubsystemLoader
from InsightUtilities import InsightSingleton, ConfigLoader
import InsightLogger
import discord_bot


class SubsystemBase(metaclass=InsightSingleton):
    def __init__(self, subsystemloader):
        self.lg = InsightLogger.InsightLogger.get_logger('Subsystem.{}'.format(self.__class__.__name__),
                                                         'Subsystem.log', child=True)
        self.subsystems: SubsystemLoader = subsystemloader
        self.loop = self.subsystems.client.loop
        self.client: discord_bot.Discord_Insight_Client = self.subsystems.client
        self.service = self.subsystems.service
        self.zk = self.service.zk_obj
        self.config: ConfigLoader = ConfigLoader()

    async def start_subsystem(self):
        print("Starting subsystem: {}".format(self.__class__.__name__))

    async def stop_subsystem(self):
        print("Stopping subsystem: {}".format(self.__class__.__name__))
