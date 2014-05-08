import mock

from piper.core import Piper
from piper.utils import DotDict

from test.utils import builtin


class PiperTestBase(object):
    def setup_method(self, method):
        self.piper = Piper()


class TestPiperSetup(PiperTestBase):
    def setup_method(self, method):
        self.methods = (
            'load_config',
            'validate_config',
        )

        super(TestPiperSetup, self).setup_method(method)

    def test_setup_calls(self):
        for method in self.methods:
            setattr(self.piper, method, mock.MagicMock())

        self.piper.setup()

        for method in self.methods:
            getattr(self.piper, method).assert_called_once_with()


class TestPiperConfigLoader(PiperTestBase):
    def setup_method(self, method):
        self.data = 'lel: 10\ntest: wizard\n\n'
        super(TestPiperConfigLoader, self).setup_method(method)

    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_no_file(self, isfile, exit):
        isfile.return_value = False
        self.piper.load_config()

        exit.assert_called_once_with(127)

    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_invalid_yaml(self, isfile, exit):
        isfile.return_value = True
        fake = mock.mock_open(read_data='{')

        with mock.patch(builtin('open'), fake):
            self.piper.load_config()

        exit.assert_called_once_with(126)

    @mock.patch('yaml.safe_load')
    @mock.patch('os.path.isfile')
    def test_load_config_actual_load(self, isfile, sl):
        isfile.return_value = True
        fake = mock.mock_open(read_data=str(self.data))

        with mock.patch(builtin('open'), fake):
            self.piper.load_config()

        sl.assert_called_once_with(fake.return_value.read.return_value)
        assert self.piper.raw_config == sl.return_value
        assert isinstance(self.piper.config, DotDict)
        assert self.piper.config.data == sl.return_value
