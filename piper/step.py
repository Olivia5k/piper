import logbook

from piper.utils import DotDict


class Step(object):
    """
    An execution step.

    This base implementation will execute whatever command line is set in the
    configuration.

    """

    def __init__(self, conf, index):
        self.conf = DotDict(conf)

        # Index of execution order. Added by the runner when parsing the
        # config file.
        self.index = index

        self.log = logbook.Logger(
            '{0}-{1}'.format(self.__class__.__name__, self.index)
        )

    def execute(self):
        """
        The main entry point.

        This is what Env()s are supposed to run.

        """

        self.pre()
        self.run()
        self.post()

    def pre(self):  # pragma: nocover
        pass

    def run(self):  # pragma: nocover
        pass

    def post(self):  # pragma: nocover
        pass
