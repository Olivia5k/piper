import logbook


class VCSBase(object):
    def __init__(self, name, root_url):
        self.name = name
        self.root_url = root_url

        self.log = logbook.Logger('{0}: {1}'.format(
            self.__class__.__name__, self.name
        ))

    def get_project(self, project):
        raise NotImplementedError()
