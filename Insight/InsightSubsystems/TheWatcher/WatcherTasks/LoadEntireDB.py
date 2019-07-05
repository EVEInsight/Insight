from InsightSubsystems.TheWatcher.WatcherTasks import WatcherTask
from database.db_tables import tb_kills
from sqlalchemy.orm import Session
import InsightLogger


class LoadEntireDB(WatcherTask.WatcherTask):
    def __init__(self, watcher_main):
        super().__init__(watcher_main)
        self.chunk_size = self.service.config_file.getint("TheWatcher", "chunk_size", fallback=20000)

    def get_km_chunk(self, starting_id):
        db: Session = self.service.get_session()
        rows = []
        try:
            c_size = self.chunk_size
            st = InsightLogger.InsightLogger.time_start()
            rows = db.query(tb_kills).order_by(tb_kills.kill_id.desc()).filter(tb_kills.kill_id < starting_id).limit(c_size).all()
            InsightLogger.InsightLogger.time_log(self.logger, st, "Query for KM chunk of size: {}".format(len(rows)),
                                                 seconds=True)
        except Exception as ex:
            print(ex)
            self.logger.exception(ex)
        finally:
            db.close()
            return rows

    def _run_task(self):
        self.logger.info("Starting KM enqueue chunk gatherer.")
        g_st = InsightLogger.InsightLogger.time_start()
        index_max_id = 9e9
        total_submit = 0
        while True:
            rows = self.get_km_chunk(index_max_id)
            if len(rows) == 0:
                break
            enq_st = InsightLogger.InsightLogger.time_start()
            for km in rows:
                if km.kill_id < index_max_id:
                    index_max_id = km.kill_id
                self.watcher.submit_km_sync_block(km)
                total_submit += 1
            InsightLogger.InsightLogger.time_log(self.logger, enq_st, "Enqueue chunk size: {}".format(len(rows)),
                                                 seconds=True)
        InsightLogger.InsightLogger.time_log(self.logger, g_st, "Completed enqueue of {} KMs from DB.".format(
            total_submit), seconds=True)
