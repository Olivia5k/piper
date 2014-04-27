import mock

from piper.core import Piper


class PiperTestBase(object):
    def setup_method(self, method):
        self.piper = Piper()


class TestPiperSetup(PiperTestBase):
    def test_setup_calls(self):
        self.piper.load_config = mock.MagicMock()

        self.piper.setup()

        self.piper.load_config.assert_called_once_with()


class TestPiperConfigLoader(PiperTestBase):
    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_no_file(self, isfile, exit):
        isfile.return_value = False
        self.piper.load_config()

        exit.assert_called_once_with(127)
