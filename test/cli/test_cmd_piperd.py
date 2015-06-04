from piper.cli import cmd_piperd
from piper import api
from piper import agent
from piper.db import core as db
from piper import config

import mock


class TestEntry:
    @mock.patch('piper.cli.cmd_piperd.CLI')
    def test_calls(self, clibase):
        self.mock = mock.Mock()
        cmd_piperd.entry(self.mock)
        clibase.assert_called_once_with(
            'piperd',
            (
                api.ApiCLI,
                db.DbCLI,
                agent.AgentCLI,
            ),
            config.AgentConfig,
            args=self.mock
        )
        clibase.return_value.entry.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piperd.CLI')
    def test_return_value(self, clibase):
        ret = cmd_piperd.entry()
        assert ret is clibase.return_value.entry.return_value
