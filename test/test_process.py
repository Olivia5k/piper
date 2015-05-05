import sh

from piper.process import Process

import mock


class TestProcessSetup:
    def setup_method(self, method):
        self.proc = Process(mock.Mock(), '/usr/bin/empathy world hide', 'key')

    @mock.patch('sh.Command')
    def test_setup(self, sh_mock):
        self.proc.setup()

        assert sh_mock.called_once_with('/usr/bin/empathy')


class TestProcessRun:
    def test_run_failure(self):
        self.proc = Process(mock.Mock(), 'ls -l', 'oioi')
        self.proc.sh = mock.MagicMock()
        self.proc.sh.side_effect = sh.ErrorReturnCode
        self.proc.run()
        assert self.proc.success is False

    def test_run_success(self):
        self.proc = Process(mock.Mock(), 'ls -l', 'oioi')
        self.proc.sh = mock.MagicMock()
        self.proc.sh.exit_code = 0
        self.proc.run()
        assert self.proc.success is True
