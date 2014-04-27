import mock

from piper.core import Piper


class TestPiperConfigLoader(object):
    def setup_method(self, method):
        self.piper = Piper()

    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_no_file(self, isfile, exit):
        isfile.return_value = False
        self.piper.load_config()

        exit.assert_called_once_with(127)
