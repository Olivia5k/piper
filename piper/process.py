import logbook


class Process(object):
    """
    Helper class for running processes

    """

    def __init__(self, cmd):
        self.success = None
        self.log = logbook.Logger(self.__class__.__name__)

    def run(self):
        pass
