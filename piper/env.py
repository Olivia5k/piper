import tempfile
import shutil
from piper.utils import DotDict


class Environment(DotDict):
    def setup(self):  # pragma: nocover
        pass

    def teardown(self):  # pragma: nocover
        pass

    def execute(self, step):
        raise NotImplementedError()


class TempDirEnvironment(Environment):
    """
    Example implementation of an environment, probably useful as well

    Does the build in a temporary directory as done by the tempfile module.
    Once build is done, the temporary directory is removed unless specified
    to be kept.

    """

    def setup(self):
        self.dir = tempfile.mkdtemp()

    def teardown(self):
        if self.delete_when_done:
            shutil.rmtree(self.dir)

    def execute(self, step):
        raise NotImplementedError()
