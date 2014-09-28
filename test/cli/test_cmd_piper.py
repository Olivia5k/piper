from piper import build
from piper.db import core as db
from piper.cli import cmd_piper

import mock


class TestEntry(object):
    @mock.patch('piper.cli.cmd_piper.CLIBase')
    def test_calls(self, clibase):
        self.mock = mock.Mock()
        cmd_piper.entry(self.mock)
        clibase.assert_called_once_with(
            'piper',
            (build.ExecCLI, db.DbCLI),
            args=self.mock
        )
        clibase.return_value.entry.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piper.CLIBase')
    def test_return_value(self, clibase):
        ret = cmd_piper.entry()
        assert ret is clibase.return_value.entry.return_value
