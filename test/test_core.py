import jsonschema
import mock
import pytest

from piper.core import Piper
from piper.utils import DotDict

from test.utils import builtin


class PiperTestBase(object):
    def setup_method(self, method):
        self.piper = Piper(mock.Mock(), mock.Mock())
        self.base_config = {
            'version': '0.0.1-alpha1',
            'jobs': {'test': ['test'], 'build': ['test', 'build']},
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
            'configure_env',
            'configure_steps',
            'configure_job',
            'setup_env',
        )

        super(TestPiperSetup, self).setup_method(method)

    def test_setup_calls(self):
        for method in self.methods:
            setattr(self.piper, method, mock.Mock())

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

    def test_no_jobs_specified(self):
        self.check_missing_key('jobs')


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


class TestPiperConfigureEnv(object):
    def setup_method(self, method):
        self.env_key = 'local'
        self.cls_key = 'unisonic.KingForADay'
        self.cls = mock.Mock()

        self.piper = Piper(self.env_key, mock.Mock())
        self.piper.classes = {self.cls_key: self.cls}
        self.piper.config = DotDict({
            'envs': {
                'local': {
                    'class': self.cls_key,
                }
            },
        })

    def test_configure_env(self):
        self.piper.configure_env()

        self.cls.assert_called_once_with(self.piper.config.envs[self.env_key])
        self.cls.return_value.validate.assert_called_once_with()


class TestPiperConfigureSteps(object):
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

        self.piper = Piper(self.step_key, mock.Mock())
        for key in self.config['steps']:
            cls = self.config['steps'][key]['class']
            self.piper.classes[cls] = mock.Mock()

        self.piper.config = DotDict(self.config)

    def test_configure_steps(self):
        self.piper.configure_steps()

        for key in self.config['steps']:
            cls_key = self.config['steps'][key]['class']

            cls = self.piper.classes[cls_key]
            cls.assert_called_once_with(key, self.piper.config.steps[key])
            cls.return_value.validate.assert_called_once_with()


class TestPiperConfigureJob(object):
    def setup_method(self, method):
        self.job_key = 'mmmbop'
        self.step_keys = ('bidubidappa', 'dubop')
        self.steps = (mock.Mock(), mock.Mock())

        for step in self.steps:
            step.config.depends = None

        self.config = {
            'jobs': {
                self.job_key: self.step_keys,
            },
        }

    def get_piper(self, config):
        piper = Piper(mock.Mock(), self.job_key)
        piper.steps = dict(zip(self.step_keys, self.steps))
        piper.config = DotDict(config)
        return piper

    def test_configure_job(self):
        self.piper = self.get_piper(self.config)
        self.piper.configure_job()

        for x, _ in enumerate(self.step_keys):
            assert self.piper.order[x] is self.steps[x]

    def test_configure_job_with_dependency(self):
        """
        Set so that we only have a list with the second item, and set so that
        it depends on the first. This should add the first item to the ordered
        list even though it's not otherwise specified.

        """

        self.steps[1].config.depends = self.step_keys[0]
        self.piper = self.get_piper({
            'jobs': {
                self.job_key: self.step_keys[1:2],
            },
        })

        self.piper.configure_job()

        assert len(self.piper.order) == 2
        assert self.piper.order[0] is self.steps[0]
        assert self.piper.order[1] is self.steps[1]

    def test_configure_job_with_multiple_dependencies(self):
        """
        Set so that we see that a step with multiple dependencies gets all of
        them set.

        """

        # Add a new step and let it depend on the two earlier ones
        key = 'schuwappa'
        self.step_keys += (key,)
        root = mock.Mock()
        root.config.depends = self.step_keys[0:2]
        self.steps += (root,)

        self.piper = self.get_piper({
            'jobs': {
                self.job_key: (key,),
            },
        })

        self.piper.configure_job()

        assert len(self.piper.order) == 3
        assert self.piper.order[0] is self.steps[0]
        assert self.piper.order[1] is self.steps[1]
        assert self.piper.order[2] is self.steps[2]


class TestPiperExecute(object):
    def setup_method(self, method):
        self.piper = Piper(mock.Mock(), mock.Mock())
        self.piper.order = [mock.Mock() for _ in range(3)]
        self.piper.env = mock.Mock()

    def test_all_successful(self):
        self.piper.execute()

        calls = [mock.call(step) for step in self.piper.order]
        assert self.piper.env.execute.call_args_list == calls
        assert self.piper.success is True

    def test_execution_stops_by_failed_step(self):
        self.piper.order[1].success = False
        self.piper.env.execute.side_effect = (
            mock.Mock(),
            mock.Mock(success=False),
        )
        self.piper.execute()

        calls = [mock.call(step) for step in self.piper.order[:2]]
        assert self.piper.env.execute.call_args_list == calls
        assert self.piper.success is False


class TestPiperSetupEnv(PiperTestBase):
    def setup_method(self, method):
        super(TestPiperSetupEnv, self).setup_method(method)
        self.piper.env = mock.Mock()

    def test_setup_env(self):
        self.piper.setup_env()
        self.piper.env.setup.assert_called_once_with()


class TestPiperTeardown(PiperTestBase):
    def setup_method(self, method):
        super(TestPiperTeardown, self).setup_method(method)
        self.piper.env = mock.Mock()

    def test_teardown(self):
        self.piper.teardown_env = mock.Mock()
        self.piper.teardown()
        self.piper.teardown_env.assert_called_once_with()

    def test_teardown_env(self):
        self.piper.teardown_env()
        self.piper.env.teardown.assert_called_once_with()
