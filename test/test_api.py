from piper.api import ApiCLI

import mock


class TestApiCLISetup(object):
    def setup_method(self, method):
        ...


class TestApiCLIRun(object):
    def setup_method(self, method):
        self.config = mock.Mock()

        self.cli = ApiCLI(self.config)
        self.cli.setup = mock.Mock()
        self.cli.loop = mock.Mock()

    def test_calls(self):
        self.cli.run()
        self.cli.loop.run_forever.assert_called_once_with()
