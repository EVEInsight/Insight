import os
import traceback


class InsightUpdater(object):
    @classmethod
    def insight_update(cls, multiproc_dict: dict):
        try:
            from git import Repo, InvalidGitRepositoryError
            dir_self = os.path.abspath(os.getcwd())
            print('Insight is now attempting to automatically update the path: {}'.format(dir_self))
            try:
                r = Repo(dir_self)
                if r.remotes.origin.url == 'https://github.com/Nathan-LS/Insight.git':
                    h = r.head.object
                    r.git.pull()
                    nh = r.head.object
                    if h == nh:
                        multiproc_dict['notify_msg'] = 'There are no new updates to apply.'
                    else:
                        multiproc_dict['notify_msg'] = 'Insight has been updated from:\n{} - {}\n{}\n' \
                                                            'to\n\n{} - {}\n{}\n'.format(h.committed_datetime, h.hexsha,
                                                                                     h.message, nh.committed_datetime,
                                                                                     nh.hexsha, nh.message)
                else:
                    multiproc_dict['notify_msg'] = 'Invalid repo. Found repo but it is not an Insight repo.'
            except InvalidGitRepositoryError:
                multiproc_dict['notify_msg'] = "Unable to update versions of Insight that don't use Git. If you are " \
                                                    "running the bin version of Insight you must manually download the " \
                                                    "latest release from Github."
        except Exception as ex:
            msg = traceback.format_exc()
            multiproc_dict['notify_msg'] = "Update failed. Error when updating: \n\n{}".format(msg[:1750])
        print(multiproc_dict.get('notify_msg'))
