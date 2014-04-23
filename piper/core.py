from piper.utils import DotDict


class Environment(DotDict):
    def setup(self):
        pass

    def teardown(self):
        pass

    def execute(self):
        raise NotImplementedError()
