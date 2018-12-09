from pympler import summary, muppy
import InsightLogger


class MemTracker(object):
    def __init__(self):
        self.logger = InsightLogger.InsightLogger.get_logger('MemTracker', 'MemTracker.log')
        self.previous_summary = None

    def str_print_(self, rows, limit=15, sort='size', order='descending'):
        """helper function to redirect output from pympler from stdout to string"""
        str_output = ""
        for line in summary.format_(rows, limit=limit, sort=sort, order=order):
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
