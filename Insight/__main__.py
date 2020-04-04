import sys
import multiprocessing
import InsightMain
import datetime


class Main(object):
    @classmethod
    def main(cls):
        manager = multiprocessing.Manager()
        shared_dict = manager.dict()
        shared_dict['flag_reboot'] = True
        crash_count = 0
        crash_count_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        while shared_dict.get('flag_reboot') is True:
            shared_dict['flag_reboot'] = False
            shared_dict['flag_update'] = False
            shared_dict['crash_recovery'] = False
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
                crash_count += 1
                if shared_dict.get('crash_recovery') is True and crash_count < 3:
                    if datetime.datetime.utcnow() > crash_count_time:
                        crash_count = 0
                        crash_count_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                    print('Insight exited with code: {} and is attempting to reboot via crash recovery.'
                          ''.format(p1.exitcode))
                    shared_dict['notify_msg'] = 'Insight exited with exit code: {} and has successfully rebooted.' \
                                                ''.format(p1.exitcode)
                    shared_dict['flag_reboot'] = True
                    continue
                print('Insight exited with exit code: {}'.format(p1.exitcode))
                shared_dict['flag_reboot'] = False
                sys.exit(p1.exitcode)
            else:
                if shared_dict['flag_reboot'] is True:
                    print('Insight is rebooting.')
                    shared_dict['notify_msg'] = 'Insight successfully rebooted.'
                else:
                    break


if __name__ == "__main__":
    multiprocessing.freeze_support()
    Main.main()
