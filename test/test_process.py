import subprocess as sub

from piper.process import Process

import mock


class TestProcessSetup(object):
    def setup_method(self, method):
        self.proc = Process(mock.Mock(), '/usr/bin/empathy world hide', 'key')

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
            'poll': mock.Mock(side_effect=[False, False, True]),
            'stdout': mock.Mock(),
            'stderr': mock.Mock(),
            'wait': mock.Mock(),
        }

        self.proc = Process(mock.Mock(), '', 'key')

        # Lines should be read twice since we have two successful poll()s in
        # the default setup
        self.readline_calls = [mock.call(), mock.call()]

    def test_run_successfully(self):
        self.proc.popen = mock.Mock(**self.mocks)
        self.mocks['wait'].return_value = 0
        self.proc.run()

        assert self.mocks['stdout'].readline.call_args_list == \
            self.readline_calls

        self.mocks['wait'].assert_called_once_with()
        assert self.proc.success is True

    def test_run_failure(self):
        self.proc.popen = mock.Mock(**self.mocks)
        self.mocks['wait'].return_value = 1
        self.proc.run()

        assert self.mocks['stdout'].readline.call_args_list == \
            self.readline_calls
        self.mocks['wait'].assert_called_once_with()
        assert self.proc.success is False

        # Stderr should've been dumped
        self.mocks['stderr'].read.assert_called_once_with()

    def test_run_abort_on_no_stdout(self):
        # Prepare the mocks so that they don't abort by finishing polling, but
        # rather by exhausting stdout
        self.mocks['poll'] = mock.Mock(return_value=False)
        self.mocks['stdout'] = mock.Mock(
            readline=mock.Mock(
                side_effect=[b'cell', b'block', b'tango', b'']
            )
        )

        self.proc.popen = mock.Mock(**self.mocks)
        self.proc.run()

        assert self.mocks['stdout'].readline.call_count == 4

    def test_dry_run_does_not_execute(self):
        self.proc.popen = mock.Mock()
        self.proc.ns.dry_run = True
        self.proc.run()

        assert self.proc.popen.poll.call_count == 0
        assert self.proc.success is True
