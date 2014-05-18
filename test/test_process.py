import subprocess as sub

from piper.process import Process

import mock


class TestProcessSetup(object):
    def setup_method(self, method):
        self.proc = Process('/usr/bin/empathy world hide')

    @mock.patch('subprocess.Popen')
    def test_setup(self, popen):
        self.proc.setup()

        popen.assert_called_once_with(
            ['/usr/bin/empathy', 'world', 'hide'],
            stdout=sub.PIPE,
            stderr=sub.PIPE,
        )


class TestProcessRun(object):
    def setup_method(self, method):
        self.mocks = {
            'poll': mock.MagicMock(side_effect=[False, False, True]),
            'stdout': mock.MagicMock(),
            'stderr': mock.MagicMock(),
            'wait': mock.MagicMock(),
        }

        self.proc = Process('')

        # Lines should be read twice since we have two successful poll()s in
        # the default setup
        self.readline_calls = [mock.call(), mock.call()]

    def test_run_successfully(self):
        self.proc.popen = mock.MagicMock(**self.mocks)
        self.mocks['wait'].return_value = 0
        self.proc.run()

        assert self.mocks['stdout'].readline.call_args_list == \
            self.readline_calls

        self.mocks['wait'].assert_called_once_with()
        self.proc.success is True

    def test_run_failure(self):
        self.proc.popen = mock.MagicMock(**self.mocks)
        self.mocks['wait'].return_value = 1
        self.proc.run()

        assert self.mocks['stdout'].readline.call_args_list == \
            self.readline_calls
        self.mocks['wait'].assert_called_once_with()
        self.proc.success is False

        # Stderr should've been dumped
        self.mocks['stderr'].read.assert_called_once_with()

    def test_run_abort_on_no_stdout(self):
        # Prepare the mocks so that they don't abort by finishing polling, but
        # rather by exhausting stdout
        self.mocks['poll'] = mock.MagicMock(return_value=False)
        self.mocks['stdout'] = mock.MagicMock(
            readline=mock.MagicMock(
                side_effect=[b'cell', b'block', b'tango', b'']
            )
        )

        self.proc.popen = mock.MagicMock(**self.mocks)
        self.proc.run()

        assert self.mocks['stdout'].readline.call_count == 4
