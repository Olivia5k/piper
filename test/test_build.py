import mock

from piper.config import BuildConfig
from piper.build import Build
from piper.build import ExecCLI

from test.utils import BASE_CONFIG
from test.utils import SQLAIntegration


class BuildTestBase(object):
    def setup_method(self, method):
        self.build = Build(mock.MagicMock())
        self.base_config = BASE_CONFIG


class TestBuildSetup(BuildTestBase):
    def setup_method(self, method):
        self.methods = (
            'add_build',
            'set_logfile',
            'lock_agent',
            'set_version',

            'configure_env',
            'configure_steps',
            'configure_job',

            'setup_env',
        )

        super(TestBuildSetup, self).setup_method(method)

    def test_setup_calls(self):
        for method in self.methods:
            setattr(self.build, method, mock.Mock())

        self.build.setup()

        for method in self.methods:
            getattr(self.build, method).assert_called_once_with()


class TestBuildRun(BuildTestBase):
    def setup_method(self, method):
        self.methods = ('setup', 'execute', 'teardown', 'finish')

        super(TestBuildRun, self).setup_method(method)
        self.build.version = mock.Mock()

        for method in self.methods:
            setattr(self.build, method, mock.Mock())

    def test_run_calls(self):
        self.build.run()

        for method in self.methods:
            getattr(self.build, method).assert_called_once_with()

    def test_run_returns_boolean_success(self):
        self.build.success = False
        ret = self.build.run()
        assert ret is False

        self.build.success = True
        ret = self.build.run()
        assert ret is True


class TestBuildSetVersion(object):
    def setup_method(self, method):
        self.version = '0.0.0.0.0.0.0.0.1-beta'
        self.cls = mock.Mock()
        self.cls_key = 'mandowar.FearOfTheDark'

        self.build = Build(mock.Mock())
        self.build.config.raw = {
            'version': {
                'class': self.cls_key,
            },
        }
        self.build.config.classes = {self.cls_key: self.cls}

    def test_set_version(self):
        self.build.set_version()

        self.cls.assert_called_once_with(self.build.config.raw['version'])
        self.cls.return_value.validate.assert_called_once_with()


class TestBuildConfigureEnv(object):
    def setup_method(self, method):
        env_key = 'local'
        self.cls_key = 'unisonic.KingForADay'
        self.cls = mock.Mock()

        self.config = mock.Mock()
        self.config.env = env_key
        self.config.classes = {self.cls_key: self.cls}
        self.config.raw = {
            'envs': {
                env_key: {
                    'class': self.cls_key,
                }
            }
        }

        self.build = Build(self.config)

    def test_configure_env(self):
        self.build.configure_env()

        self.cls.assert_called_once_with(
            self.build.config.raw['envs'][self.config.env]
        )
        self.cls.return_value.validate.assert_called_once_with()


class TestBuildConfigureSteps(object):
    def setup_method(self, method):
        self.step_key = 'local'
        self.raw = {
            'steps': {
                'bang': {
                    'class': 'edguy.police.LoveTyger',
                },
                'boom': {
                    'class': 'bethhart.light.LiftsUUp',
                }
            },
        }

        self.build = Build(mock.Mock(job=self.step_key))
        self.build.config = mock.Mock()
        self.build.config.classes = {}
        self.build.config.raw = self.raw

        for key in self.raw['steps']:
            cls = self.raw['steps'][key]['class']
            self.build.config.classes[cls] = mock.Mock()

    def test_configure_steps(self):
        self.build.configure_steps()

        for key in self.raw['steps']:
            cls_key = self.raw['steps'][key]['class']

            cls = self.build.config.classes[cls_key]
            cls.assert_called_once_with(
                self.build.config.raw['steps'][key],
                key
            )
            cls.return_value.validate.assert_called_once_with()


class TestBuildConfigureJob(object):
    def setup_method(self, method):
        self.step_keys = ('bidubidappa', 'dubop', 'schuwappa')
        self.job_key = 'mmmbop'

        self.config = mock.MagicMock()
        self.config.job = self.job_key
        self.config.raw = {
            'job': self.job_key,
            'jobs': {self.job_key: self.step_keys}
        }
        self.steps = (mock.Mock(), mock.Mock(), mock.Mock())

        for step in self.steps:
            step.config.depends = None

    def get_build(self, config):
        build = Build(self.config)
        build.steps = dict(zip(self.step_keys, self.steps))
        return build

    def test_configure_job(self):
        self.build = self.get_build(self.config)
        self.build.configure_job()

        for x, _ in enumerate(self.step_keys):
            assert self.build.order[x] is self.steps[x]


class TestBuildExecute(object):
    def setup_method(self, method):
        self.build = Build(mock.Mock())
        self.build.order = [mock.Mock() for _ in range(3)]
        self.build.env = mock.Mock()

    def test_all_successful(self):
        self.build.execute()

        calls = [mock.call(step) for step in self.build.order]
        assert self.build.env.execute.call_args_list == calls
        assert self.build.success is True

    def test_execution_stops_by_failed_step(self):
        self.build.order[1].success = False
        self.build.env.execute.side_effect = (
            mock.Mock(),
            mock.Mock(success=False),
        )
        self.build.execute()

        calls = [mock.call(step) for step in self.build.order[:2]]
        assert self.build.env.execute.call_args_list == calls
        assert self.build.success is False


class TestBuildSetupEnv(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildSetupEnv, self).setup_method(method)
        self.build.env = mock.Mock()

    def test_setup_env(self):
        self.build.setup_env()
        self.build.env.setup.assert_called_once_with()


class TestBuildTeardown(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildTeardown, self).setup_method(method)
        self.build.env = mock.Mock()

    def test_teardown(self):
        self.build.teardown_env = mock.Mock()
        self.build.teardown()
        self.build.teardown_env.assert_called_once_with()

    def test_teardown_env(self):
        self.build.teardown_env()
        self.build.env.teardown.assert_called_once_with()


class TestBuildAddBuild(BuildTestBase):
    def test_add_build(self):
        self.build.db = mock.Mock()
        self.build.add_build()

        assert self.build.ref is self.build.db.add_build.return_value
        self.build.db.add_build.assert_called_once_with(self.build)


class TestBuildFinish(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildFinish, self).setup_method(method)
        self.build.db = mock.Mock()
        self.build.log_handler = mock.Mock()

    @mock.patch('ago.human')
    @mock.patch('piper.utils.now')
    def test_build_is_updated_in_database(self, now, human):
        self.build.finish()

        assert self.build.end is now.return_value
        now.assert_called_once_with()
        self.build.db.update_build.assert_called_once_with(
            self.build,
            ended=now.return_value
        )


class TestBuildSetLogfile(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildSetLogfile, self).setup_method(method)
        self.build.ref = mock.Mock()
        self.build.log_handler = mock.Mock()

    @mock.patch('piper.logging.get_file_logger')
    def test_logger_is_set(self, gfl):
        self.build.log = None
        self.build.set_logfile()
        assert self.build.log is not None

    @mock.patch('piper.logging.get_file_logger')
    def test_logfile_is_set(self, gfl):
        self.build.logfile = None
        self.build.set_logfile()
        assert self.build.logfile is not None

    @mock.patch('piper.logging.get_file_logger')
    def test_log_handler_is_configured(self, gfl):
        self.build.set_logfile()
        assert gfl.call_count == 1
        assert gfl.return_value is self.build.log_handler
        self.build.log_handler.push_application.assert_called_once_with()


class TestBuildLockAgent(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildLockAgent, self).setup_method(method)
        self.build.db = mock.Mock()

    def test_lock_db_call(self):
        self.build.lock_agent()
        self.build.db.lock_agent.assert_called_once_with(self.build)


class TestBuildUnlockAgent(BuildTestBase):
    def setup_method(self, method):
        super(TestBuildUnlockAgent, self).setup_method(method)
        self.build.db = mock.Mock()

    def test_lock_db_call(self):
        self.build.unlock_agent()
        self.build.db.unlock_agent.assert_called_once_with(self.build)


class TestExecCLIRun(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = ExecCLI(self.config)

    @mock.patch('piper.build.Build')
    def test_calls(self, b):
        ret = self.cli.run()

        assert ret == 0
        b.assert_called_once_with(self.config)
        b.return_value.run.assert_called_once_with()

    @mock.patch('piper.build.Build')
    def test_nonzero_exitcode_on_failure(self, b):
        b.return_value.run.return_value = False
        ret = self.cli.run()

        assert ret == 1


class TestBuildIntegration(SQLAIntegration):
    def setup_method(self, method):
        super(TestBuildIntegration, self).setup_method(method)
        self.raw_config = {
            'version': {
                'class': 'piper.version.StaticVersion',
                'version': '0.0.1',
            },
            'envs': {
                'local': {
                    'class': 'piper.env.EnvBase',
                }
            },
            'steps': {
                'test': {
                    'class': 'piper.step.CommandLineStep',
                    'command': 'true',
                },
            },
            'jobs': {
                'test': [
                    'test',
                ],
            },
            'db': {
                'class': 'piper.db.SQLAlchemyDB',
                'host': self.db_host,
            },
        }

        self.config = BuildConfig(raw=self.raw_config).load()

    def test_build_with_one_successful_step(self):
        self.config.job = 'test'
        self.config.env = 'local'
        self.build = Build(self.config)

        ret = self.build.run()

        assert ret is True
