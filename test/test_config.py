import jsonschema
import pytest

import mock
import copy

from piper.config import BuildConfig

from test import utils


class BuildConfigTestBase(object):
    def setup_method(self, method):
        self.config = BuildConfig()
        # Without the deepcopy the tests that check for missing keys will
        # destroy everything for everyone!
        self.base_config = copy.deepcopy(utils.BASE_CONFIG)


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


class TestBuildConfigLoadClasses(BuildConfigTestBase):
    def setup_method(self, method):
        super(TestBuildConfigLoadClasses, self).setup_method(method)
        self.config.data = self.base_config

        self.version = 'piper.version.GitVersion'
        self.step = 'piper.step.CommandLineStep'
        self.env = 'piper.env.EnvBase'
        self.db = 'piper.db.SQLAlchemyDB'

    @mock.patch('piper.config.dynamic_load')
    def test_load_classes(self, dl):
        self.config.load_classes()

        calls = (
            mock.call(self.version),
            mock.call(self.step),
            mock.call(self.env),
            mock.call(self.db),
        )
        assert dl.has_calls(calls)
        assert self.config.classes[self.version] is dl.return_value
        assert self.config.classes[self.step] is dl.return_value
        assert self.config.classes[self.env] is dl.return_value
        assert self.config.classes[self.db] is dl.return_value


class TestBuildConfigLoad(BuildConfigTestBase):
    def test_calls(self):
        self.config.load_config = mock.Mock()
        self.config.validate_config = mock.Mock()
        self.config.load_classes = mock.Mock()

        ret = self.config.load()
        assert ret is self.config

        self.config.load_config.assert_called_once_with()
        self.config.validate_config.assert_called_once_with()
        self.config.load_classes.assert_called_once_with()


class TestBuildConfigGetDatabase(BuildConfigTestBase):
    def setup_method(self, method):
        super(TestBuildConfigGetDatabase, self).setup_method(method)
        self.config.data = self.base_config
        self.db = 'piper.db.SQLAlchemyDB'
        self.mock = mock.Mock()
        self.config.classes[self.db] = self.mock

    def test_plain_run(self):
        ret = self.config.get_database()
        assert ret is self.mock.return_value
