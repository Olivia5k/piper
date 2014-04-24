from piper.utils import DotDict


class Environment(DotDict):
    def setup(self):
        pass

    def teardown(self):
        pass

    def execute(self, step):
        raise NotImplementedError()


class TempDirEnvironment(DotDict):
    """
    Example implementation of an environment, probably useful as well

    Does the build in a temporary directory as done by the tempfile module.
    Once build is done, the temporary directory is removed unless specified
    to be kept.

    """

    def setup(self):
        pass

    def teardown(self):
        pass

    def execute(self, step):
        raise NotImplementedError()
