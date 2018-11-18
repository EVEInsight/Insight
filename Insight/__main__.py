import sys
import multiprocessing
import InsightMain


class Main(object):
    @classmethod
    def main(cls):
        manager = multiprocessing.Manager()
        shared_dict = manager.dict()
        shared_dict['flag_reboot'] = True
        shared_dict['flag_update'] = False
        while shared_dict.get('flag_reboot') is True:
            shared_dict['flag_reboot'] = False
            shared_dict['flag_update'] = False
            p1 = multiprocessing.Process(target=InsightMain.InsightMain.insight_run, args=(shared_dict,))
            p1.start()
            try:
                p1.join()
            except KeyboardInterrupt:
                if p1.is_alive():
                    print('Child process is still alive. Parent waiting to force terminate process.')
                    p1.terminate()
                    p1.join()
                sys.exit(0)
            if p1.exitcode != 0:
                shared_dict['flag_reboot'] = False
                sys.exit(p1.exitcode)
            else:
                if shared_dict['flag_reboot'] is True:
                    print('Insight is rebooting.')
                    shared_dict['notify_msg'] = 'Insight successfully rebooted.'
                else:
                    break
                if shared_dict['flag_update'] is True:
                    InsightMain.InsightUpdater.insight_update(shared_dict)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    Main.main()
