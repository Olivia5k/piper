import jsonschema
import mock
import pytest

from piper.core import Piper
from piper.utils import DotDict

from test.utils import builtin


class PiperTestBase(object):
    def setup_method(self, method):
        self.piper = Piper(mock.MagicMock(), mock.MagicMock())
        self.base_config = {
            'version': '0.0.1-alpha1',
            'sets': {'test': ['test'], 'build': ['test', 'build']},
            'envs': {
                'local': {
                    'class': 'piper.env.TempDirEnv',
                    'delete_when_done': False,
                },
            },
            'steps': {
                'test': {
                    'class': 'piper.step.Step',
                    'command': '/usr/bin/env python setup.py test',
                },
                'build': {
                    'class': 'piper.step.Step',
                    'command': '/usr/bin/env python setup.py sdist',
                },
            },
        }


class TestPiperSetup(PiperTestBase):
    def setup_method(self, method):
        self.methods = (
            'load_config',
            'validate_config',
            'load_classes',
            'load_env',
            'load_steps',
            'load_set',
        )

        super(TestPiperSetup, self).setup_method(method)

    def test_setup_calls(self):
        for method in self.methods:
            setattr(self.piper, method, mock.MagicMock())

        self.piper.setup()

        for method in self.methods:
            getattr(self.piper, method).assert_called_once_with()


class TestPiperLoadConfig(PiperTestBase):
    def setup_method(self, method):
        self.data = 'lel: 10\ntest: wizard\n\n'
        super(TestPiperLoadConfig, self).setup_method(method)

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


class TestPiperValidateConfig(PiperTestBase):
    def setup_method(self, method):
        super(TestPiperValidateConfig, self).setup_method(method)
        self.piper.config = DotDict(self.base_config)

    def check_missing_key(self, key):
        del self.piper.config.data[key]
        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.piper.validate_config()

    def test_passing_validation(self):
        # Do nothing; if no exception happens, this is valid.
        self.piper.validate_config()

    def test_no_version_specified(self):
        self.check_missing_key('version')

    def test_no_envs_specified(self):
        self.check_missing_key('envs')

    def test_no_steps_specified(self):
        self.check_missing_key('steps')

    def test_no_sets_specified(self):
        self.check_missing_key('sets')


class TestPiperLoadClasses(PiperTestBase):
    def setup_method(self, method):
        super(TestPiperLoadClasses, self).setup_method(method)
        self.piper.config = DotDict(self.base_config)

        self.step = 'piper.step.Step'
        self.env = 'piper.env.TempDirEnv'

    @mock.patch('piper.core.dynamic_load')
    def test_load_classes(self, dl):
        self.piper.load_classes()

        calls = (mock.call(self.step), mock.call(self.env))
        assert dl.has_calls(calls, any_order=True)
        assert self.piper.classes[self.step] is dl.return_value
        assert self.piper.classes[self.env] is dl.return_value


class TestPiperLoadEnv(object):
    def setup_method(self, method):
        self.env_key = 'local'
        self.cls_key = 'unisonic.KingForADay'
        self.cls = mock.MagicMock()

        self.piper = Piper(self.env_key, mock.MagicMock())
        self.piper.classes = {self.cls_key: self.cls}
        self.piper.config = DotDict({
            'envs': {
                'local': {
                    'class': self.cls_key,
                }
            },
        })

    def test_load_env(self):
        self.piper.load_env()

        self.cls.assert_called_once_with(self.piper.config.envs[self.env_key])
        self.cls.return_value.validate.assert_called_once_with()


class TestPiperLoadSteps(object):
    def setup_method(self, method):
        self.step_key = 'local'
        self.config = {
            'steps': {
                'bang': {
                    'class': 'edguy.police.LoveTyger',
                },
                'boom': {
                    'class': 'bethhart.light.LiftsUUp',
                }
            },
        }

        self.piper = Piper(self.step_key, mock.MagicMock())
        for key in self.config['steps']:
            cls = self.config['steps'][key]['class']
            self.piper.classes[cls] = mock.MagicMock()

        self.piper.config = DotDict(self.config)

    def test_load_steps(self):
        self.piper.load_steps()

        for key in self.config['steps']:
            cls_key = self.config['steps'][key]['class']

            cls = self.piper.classes[cls_key]
            cls.assert_called_once_with(self.piper.config.steps[key])
            cls.return_value.validate.assert_called_once_with()


class TestPiperLoadSet(object):
    def setup_method(self, method):
        self.set_key = 'mmmbop'
        self.step_keys = ('bidubidappa', 'dubop')
        self.steps = (mock.MagicMock(), mock.MagicMock())

        self.config = {
            'sets': {
                self.set_key: self.step_keys,
            },
        }

        self.piper = Piper(mock.MagicMock(), self.set_key)
        self.piper.steps = dict(zip(self.step_keys, self.steps))
        self.piper.config = DotDict(self.config)

    def test_load_set(self):
        self.piper.load_set()

        for x, _ in enumerate(self.step_keys):
            assert self.piper.execution_order[x] is self.steps[x]


class TestPiperExecute(object):
    pass
