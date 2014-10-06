import jsonschema
import pytest
import mock

from piper.env import Env
from piper.env import TempDirEnv

from test.utils import BASE_CONFIG


class EnvTest(object):
    def setup_method(self, method):
        self.build = mock.Mock()
        self.env = Env(self.build, BASE_CONFIG['envs']['local'])
        self.step = mock.Mock()


class TestEnvSchema(EnvTest):
    def test_validate(self):
        self.env.validate()

    def test_validate_with_no_requirements(self):
        self.env.config['requirements'] = None
        self.env.validate()


class TestEnvExecute(EnvTest):
    @mock.patch('piper.env.Process')
    def test_execute_plain(self, proc):
        ret = self.env.execute(self.step)

        gc = self.step.get_command
        procobj = proc.return_value

        gc.assert_called_once_with()
        proc.assert_called_once_with(
            self.env.config,
            gc.return_value,
            self.step.log_key
        )
        procobj.run.assert_called_once_with()
        assert ret is procobj


class TestTempDirEnvSetup(object):
    def setup_method(self, method):
        self.build = mock.Mock()
        self.env = TempDirEnv(self.build, mock.MagicMock())

    @mock.patch('shutil.copytree')
    @mock.patch('os.chdir')
    @mock.patch('tempfile.mkdtemp')
    def test_setup(self, mkdtemp, chdir, copy):
        mkdtemp.return_value = '/'
        self.env.setup()

        mkdtemp.assert_called_once_with(prefix='piper-')
        chdir.assert_called_once_with(mkdtemp.return_value)
        assert self.env.dir == mkdtemp.return_value

    def test_validation_extra_field(self):
        self.env = TempDirEnv(self.build, mock.MagicMock(**{
            'class': 'hehe',
            'heart': 'black.as.night',
        }))

        with pytest.raises(jsonschema.exceptions.ValidationError):
            self.env.validate()


class TestTempDirEnvTeardown(object):
    def setup_method(self, method):
        self.build = mock.Mock()
        self.env = TempDirEnv(self.build, mock.MagicMock())
        self.env.dir = '/dir'

    @mock.patch('shutil.rmtree')
    def test_teardown_default(self, rmtree):
        self.env.dir = mock.Mock()
        self.env.config.delete_when_done = True
        self.env.teardown()

        rmtree.assert_called_once_with(self.env.dir)

    @mock.patch('shutil.rmtree')
    def test_teardown_not_permitted(self, rmtree):
        self.env.config.delete_when_done = False
        self.env.teardown()

        assert rmtree.call_count == 0


class TestTempDirEnvExecute(object):
    def setup_method(self, method):
        self.build = mock.Mock()
        self.env = TempDirEnv(self.build, mock.MagicMock())
        self.env.dir = '/'
        self.env.cwd = '/repo'
        self.step = mock.Mock()

    @mock.patch('piper.env.Process')
    @mock.patch('os.getcwd')
    def test_execute_plain(self, getcwd, proc):
        getcwd.return_value = self.env.cwd
        ret = self.env.execute(self.step)

        gc = self.step.get_command
        procobj = proc.return_value

        getcwd.assert_called_once_with()
        gc.assert_called_once_with()
        proc.assert_called_once_with(
            self.env.config,
            gc.return_value,
            self.step.log_key
        )
        procobj.run.assert_called_once_with()
        assert ret is procobj

    @mock.patch('piper.env.Process')
    @mock.patch('os.chdir')
    @mock.patch('os.getcwd')
    def test_execute_cwd_changes_back(self, getcwd, chdir, proc):
        getcwd.return_value = '/space/police'

        self.env.execute(self.step)
        getcwd.assert_called_once_with()
        chdir.assert_called_once_with(self.env.cwd)
