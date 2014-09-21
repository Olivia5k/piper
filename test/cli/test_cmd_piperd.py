from piper.cli import cmd_piperd
from piper.api import api

import mock


class TestEntry(object):
    @mock.patch('piper.cli.cmd_piperd.CLIBase')
    def test_calls(self, clibase):
        cmd_piperd.entry()
        clibase.assert_called_once_with('piperd', (api.ApiCLI,))
        clibase.return_value.entry.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piperd.CLIBase')
    def test_return_value(self, clibase):
        ret = cmd_piperd.entry()
        assert ret is clibase.return_value.entry.return_value
