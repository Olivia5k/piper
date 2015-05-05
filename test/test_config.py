import jsonschema
import pytest

import mock
import copy

from piper.config import Config
from piper.config import ConfigError
from piper.config import BuildConfig
from piper.config import AgentConfig

from test import utils


class BuildConfigTest:
    def setup_method(self, method):
        self.config = BuildConfig()
        # Without the deepcopy the tests that check for missing keys will
        # destroy everything for everyone!
        self.base_config = copy.deepcopy(utils.BASE_CONFIG)


class AgentConfigTest:
    def setup_method(self, method):
        self.config = AgentConfig()
        self.config.raw = copy.deepcopy(utils.AGENT_CONFIG)


class TestConfigLoad:
    def test_raw_configuration(self):
        self.raw = {
            'tiger army': 'pain',
        }
        self.config = Config(raw=self.raw)
        self.config.load_config = mock.Mock()
        self.config.validate_config = mock.Mock()  # Config() has no schema

        self.config.load()

        assert self.config.load_config.call_count == 0
        assert self.config.raw == self.raw


class TestConfigCollectClasses:
    def test_load_classes_loads_nested(self):
        self.raw = {
            'avantasia': {
                'class': 'seven.angels',
            },
            'opera': {
                'vandroy': {
                    'class': 'million.empty.brains',
                },
                'gabriel': {
                    'class': 'million.empty.brains',
                },
            },
        }
        self.config = Config(raw=self.raw)

        ret = self.config.collect_classes()
        assert ret == set(['seven.angels', 'million.empty.brains'])


class TestBuildConfigLoadConfig(BuildConfigTest):
    def setup_method(self, method):
        self.data = 'lel: 10\ntest: wizard\n\n'
        super(TestBuildConfigLoadConfig, self).setup_method(method)

    @mock.patch('os.path.isfile')
    def test_load_config_no_file(self, isfile):
        isfile.return_value = False
        with pytest.raises(ConfigError):
            self.config.load_config()

    @mock.patch('os.path.isfile')
    def test_load_config_invalid_yaml(self, isfile):
        isfile.return_value = True
        fake = mock.mock_open(read_data='{')

        with mock.patch(utils.builtin('open'), fake):
            with pytest.raises(ConfigError):
                self.config.load_config()

    @mock.patch('yaml.safe_load')
    @mock.patch('os.path.isfile')
    def test_load_config_actual_load(self, isfile, sl):
        isfile.return_value = True
        fake = mock.mock_open(read_data=str(self.data))

        with mock.patch(utils.builtin('open'), fake):
            self.config.load_config()

        sl.assert_called_once_with(fake.return_value.read.return_value)
        assert self.config.raw == sl.return_value


class TestBuildConfigValidateConfig(BuildConfigTest):
    def setup_method(self, method):
        super(TestBuildConfigValidateConfig, self).setup_method(method)
        self.config.raw = self.base_config

    def check_missing_key(self, key):
        del self.config.raw[key]
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

    def test_no_pipelines_specified(self):
        self.check_missing_key('pipelines')


class TestBuildConfigLoadClasses(BuildConfigTest):
    def setup_method(self, method):
        super(TestBuildConfigLoadClasses, self).setup_method(method)
        self.config.raw = self.base_config

        self.version = 'piper.version.GitVersion'
        self.step = 'piper.step.CommandLineStep'
        self.env = 'piper.env.Env'
        self.db = 'piper.db.RethinkDB'

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


class TestBuildConfigLoad(BuildConfigTest):
    def test_calls(self):
        self.config.load_config = mock.Mock()
        self.config.validate_config = mock.Mock()
        self.config.load_classes = mock.Mock()

        ret = self.config.load()
        assert ret is self.config

        self.config.load_config.assert_called_once_with()
        self.config.validate_config.assert_called_once_with()
        self.config.load_classes.assert_called_once_with()


class TestBuildConfigGetDatabase(BuildConfigTest):
    def setup_method(self, method):
        super(TestBuildConfigGetDatabase, self).setup_method(method)
        self.config.raw = self.base_config
        self.db = 'piper.db.RethinkDB'
        self.mock = mock.Mock()
        self.config.classes[self.db] = self.mock

    def test_plain_run(self):
        ret = self.config.get_database()
        assert ret is self.mock.return_value


class TestBuildConfigMergeNamespace(BuildConfigTest):
    def setup_method(self, method):
        super(TestBuildConfigMergeNamespace, self).setup_method(method)
        self.correct = 'happy for the rest of your life'

        # Can't use mocks because they have, like, a million properties.
        class FakeNS:
            key = self.correct
            _internal = 'never make a pretty woman your wife'

        self.ns = FakeNS()

    def test_filtering(self):
        self.config.merge_namespace(self.ns)

        assert self.config.key == self.correct
        assert not hasattr(self.config, '_internal')


class TestAgentConfigValidateConfig(AgentConfigTest):
    def check_missing_key(self, key):
        del self.config.raw[key]
        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.config.validate_config()

    def test_passing_validation(self):
        # Do nothing; if no exception happens, this is valid.
        self.config.validate_config()

    def test_no_agent_config(self):
        self.check_missing_key('agent')

    def test_no_db_config(self):
        self.check_missing_key('db')


class TestAgentConfigCollectClasses(AgentConfigTest):
    def test_collection(self):
        ret = self.config.collect_classes()
        assert ret == set(['piper.db.RethinkDB', 'piper.prop.FacterProp'])
