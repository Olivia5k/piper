import pytest
import mock

from piper.env import Environment
from piper.env import TempDirEnvironment


class TestEnvironment(object):
    def setup_method(self, method):
        self.env = Environment({})

    def test_execute_raises_notimplemented(self):
        with pytest.raises(NotImplementedError):
            self.env.execute(mock.MagicMock())


class TestTempDirEnvironment(object):
    def setup_method(self, method):
        self.env = TempDirEnvironment({})

    @mock.patch('tempfile.mkdtemp')
    def test_setup(self, mkdtemp):
        self.env.setup()

        mkdtemp.assert_called_once_with()
        assert self.env.dir == mkdtemp.return_value

    @mock.patch('shutil.rmtree')
    def test_teardown_default(self, rmtree):
        self.env.dir = mock.MagicMock()
        self.env.delete_when_done = True
        self.env.teardown()

        rmtree.assert_called_once_with(self.env.dir)

    @mock.patch('shutil.rmtree')
    def test_teardown_not_permitted(self, rmtree):
        self.env.delete_when_done = False
        self.env.teardown()

        assert rmtree.call_count == 0
