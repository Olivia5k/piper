from piper.cli import cmd_piperd
from piper.api import api

import mock


class TestEntry(object):
    @mock.patch('piper.cli.cmd_piperd.CLIBase')
    def test_calls(self, clibase):
        self.mock = mock.Mock()
        cmd_piperd.entry(self.mock)
        clibase.assert_called_once_with(
            'piperd',
            (api.ApiCLI,),
            args=self.mock
        )
        clibase.return_value.entry.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piperd.CLIBase')
    def test_return_value(self, clibase):
        ret = cmd_piperd.entry()
        assert ret is clibase.return_value.entry.return_value


class TestEntryIntegration(object):
    @mock.patch('piper.api.api.Flask')
    def test_api_start(self, flask):
        cmd_piperd.entry(['api', 'start'])
        flask.return_value.run.assert_called_once_with(debug=True)
