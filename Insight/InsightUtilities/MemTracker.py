from pympler import summary, muppy
import InsightLogger


class MemTracker(object):
    def __init__(self):
        self.logger = InsightLogger.InsightLogger.get_logger('MemTracker', 'MemTracker.log')
        self.previous_summary = None

    @classmethod
    def str_print_(cls, rows, limit=15, sort='size', order='descending'):
        """helper function to redirect output from pympler from stdout to string"""
        total_objects = 0
        total_memory = 0
        for r in rows:
            total_objects += r[1]
            total_memory += r[2]
        str_output = "Total Objects: {:,} Total Mem: {:,.2f} MB\n".format(total_objects, total_memory / (1024 * 1024))
        str_output += "Sorted by mem size\n"
        for line in summary.format_(rows, limit=limit, sort=sort, order=order):
            str_output += line + '\n'
        str_output += "Sorted by total amount\n"
        for line in summary.format_(rows, limit=limit, sort='#', order=order):
            str_output += line + '\n'
        return str_output

    def log_summary(self):
        summary_str = '\n\n=====Total Memory Stats=====\n'
        current_summary = summary.summarize(muppy.get_objects())
        summary_str += self.str_print_(current_summary, limit=25)
        if self.previous_summary is None:
            self.previous_summary = current_summary
        else:
            summary_str += '\n\n===== Difference since last update =====\n'
            diff = summary.get_diff(self.previous_summary, current_summary)
            summary_str += self.str_print_(diff, limit=25)
            self.previous_summary = current_summary
        self.logger.info(summary_str)

    @classmethod
    def summary(cls):
        lg = InsightLogger.InsightLogger.get_logger('MemTracker', 'MemTracker.log')
        sm = '=====Total Memory Stats=====\n' + cls.str_print_(summary.summarize(muppy.get_objects()), limit=25)
        lg.info("Admin requested memory summary\n\n{}".format(sm))
        return sm
