import jsonschema
import pytest

import mock

from piper.config import BuildConfig
from piper.utils import DotDict

from test import utils


class BuildConfigTestBase(object):
    def setup_method(self, method):
        self.config = BuildConfig()
        self.base_config = utils.BASE_CONFIG


class TestBuildConfigLoadConfig(BuildConfigTestBase):
    def setup_method(self, method):
        self.data = 'lel: 10\ntest: wizard\n\n'
        super(TestBuildConfigLoadConfig, self).setup_method(method)

    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_no_file(self, isfile, exit):
        isfile.return_value = False
        self.config.load_config()

        exit.assert_called_once_with(127)

    @mock.patch('sys.exit')
    @mock.patch('os.path.isfile')
    def test_load_config_invalid_yaml(self, isfile, exit):
        isfile.return_value = True
        fake = mock.mock_open(read_data='{')

        with mock.patch(utils.builtin('open'), fake):
            self.config.load_config()

        exit.assert_called_once_with(126)

    @mock.patch('yaml.safe_load')
    @mock.patch('os.path.isfile')
    def test_load_config_actual_load(self, isfile, sl):
        isfile.return_value = True
        fake = mock.mock_open(read_data=str(self.data))

        with mock.patch(utils.builtin('open'), fake):
            self.config.load_config()

        sl.assert_called_once_with(fake.return_value.read.return_value)
        assert self.config.raw_config == sl.return_value
        assert isinstance(self.config.config, DotDict)
        assert self.config.config.data == sl.return_value


class TestBuildConfigValidateConfig(BuildConfigTestBase):
    def setup_method(self, method):
        super(TestBuildConfigValidateConfig, self).setup_method(method)
        self.config.raw_config = self.base_config

    def check_missing_key(self, key):
        del self.config.raw_config[key]
        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.config.validate_config()

    def test_passing_validation(self):
        # Do nothing; if no exception happens, this is valid.
        self.config.validate_config()

    def test_no_version_specified(self):
        self.check_missing_key('version')

    def test_no_envs_specified(self):
        self.check_missing_key('envs')

    def test_no_steps_specified(self):
        self.check_missing_key('steps')

    def test_no_jobs_specified(self):
        self.check_missing_key('jobs')
