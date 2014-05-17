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
