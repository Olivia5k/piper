import sh

from piper.process import Process

from mock import Mock
from mock import MagicMock
from mock import patch
import pytest


@pytest.fixture
def proc():
    proc = Process(Mock(), '/path/to/cmd', 'logkey')
    proc.sh = MagicMock()

    return proc


class TestProcessSetup:
    def setup_method(self, method):
        self.proc = Process(Mock(), '/usr/bin/empathy world hide', 'key')

    @patch('sh.Command')
    def test_setup(self, Command):
        self.proc.setup()

        Command.assert_called_once_with('/usr/bin/empathy')


class TestProcessRun:
    def test_run_failure(self, proc):
        proc.sh.__iter__.side_effect = sh.ErrorReturnCode(
            '/cmd', MagicMock(), MagicMock()
        )
        proc.run()

        assert proc.success is False

    def test_run_success(self, proc):
        proc.sh.exit_code = 0
        proc.run()

        assert proc.success is True

    def test_run_with_output(self, proc):
        proc.sh.__iter__ = Mock(return_value=iter(['1', 'a']))
        proc.sh.exit_code = 0
        proc.run()

        assert proc.success is True
