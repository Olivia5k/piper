import logbook

from piper import utils


class VCSBase(object):
    def __init__(self, name, root_url):
        self.name = name
        self.root_url = root_url

        self.log = logbook.Logger('{0}: {1}'.format(
            self.__class__.__name__, self.name
        ))

    def get_project(self, project):
        raise NotImplementedError()

    def get_project_name(self, build):
        raise NotImplementedError()


class GitVCS(VCSBase):
    def get_project_name(self):
        name = utils.oneshot('git config remote.origin.url')
        return name.split(':')[1]
