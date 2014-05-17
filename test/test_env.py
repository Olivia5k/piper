import pytest
import mock

from piper.env import Env
from piper.env import TempDirEnv


class TestEnvExecute(object):
    def setup_method(self, method):
        self.env = Env({})

    def test_execute_raises_notimplemented(self):
        with pytest.raises(NotImplementedError):
            self.env.execute(mock.MagicMock())


class TestEnvValidate(object):
    def setup_method(self, method):
        self.env = Env({})
        self.env.config = mock.MagicMock()

    @mock.patch('jsonschema.validate')
    def test_validate(self, jv):
        self.env.validate()
        jv.assert_called_once_with(self.env.config.data, self.env.schema)


class TestTempDirEnvSetup(object):
    def setup_method(self, method):
        self.env = TempDirEnv({})

    @mock.patch('os.chdir')
    @mock.patch('tempfile.mkdtemp')
    def test_setup(self, mkdtemp, chdir):
        mkdtemp.return_value = '/'
        self.env.setup()

        mkdtemp.assert_called_once_with()
        chdir.assert_called_once_with(mkdtemp.return_value)
        assert self.env.dir == mkdtemp.return_value


class TestTempDirEnvTeardown(object):
    def setup_method(self, method):
        self.env = TempDirEnv({})

    @mock.patch('shutil.rmtree')
    def test_teardown_default(self, rmtree):
        self.env.dir = mock.MagicMock()
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
        self.env = TempDirEnv({})
        self.env.dir = '/'
        self.step = mock.MagicMock()

    @mock.patch('os.getcwd')
    def test_execute(self, getcwd):
        getcwd.return_value = self.env.dir
        self.env.execute(self.step)

        getcwd.assert_called_once_with()
        self.step.execute.assert_called_once_with()

    @mock.patch('os.chdir')
    @mock.patch('os.getcwd')
    def test_execute_cwd_changes_back(self, getcwd, chdir):
        getcwd.return_value = '/space/police'

        self.env.execute(self.step)
        self.step.execute.assert_called_once_with()
