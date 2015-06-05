from piper.cli.cli import CLI
import logbook

import mock


class TestCLIEntry:
    def setup_method(self, method):
        self.cli = CLI('test', (mock.Mock(),), mock.Mock())

        # Fake log handlers, needs to be macic mocks due to context managing
        self.cli.get_handlers = mock.Mock()
        self.cli.log_handlers = mock.MagicMock(), mock.MagicMock()

        self.cli.set_debug = mock.Mock()
        self.cli.load_config = mock.Mock()
        self.cli.config = mock.Mock()

        self.parser = mock.MagicMock()
        self.runners = mock.MagicMock()
        self.cli.build_parser = mock.Mock()
        self.cli.build_parser.return_value = self.parser, self.runners

        self.ns = self.parser.parse_args.return_value

    def test_main_entry_point(self):
        ret = self.cli.entry()

        assert ret == self.runners[self.ns.command].return_value
        self.cli.set_debug.assert_called_once_with()
        self.cli.load_config.assert_called_once_with()
        self.cli.build_parser.assert_called_once_with()

        parser, runners = self.cli.build_parser.return_value
        ns = parser.parse_args.return_value

        cmd = self.runners[self.cli.config.command]
        cmd.assert_called_once_with(ns)

        for handler in self.cli.log_handlers:
            handler.push_application.assert_called_once_with()

    def test_no_command_runs_help(self):
        self.cli.config.command = False

        ret = self.cli.entry()

        assert ret == 0
        self.parser.print_help.assert_called_once_with()


class TestCLIBuildParser:
    def setup_method(self, method):
        self.name = 'ophelia',
        self.classes = (mock.Mock(), mock.Mock())

        self.cli = CLI(self.name, self.classes, mock.Mock())

        self.cli.config = mock.Mock()
        self.cli.global_arguments = mock.Mock()
        self.cli.get_runners = mock.Mock()

    @mock.patch('argparse.ArgumentParser')
    def test_return_values(self, ap):
        parser, runners = self.cli.build_parser()

        assert parser is ap.return_value
        assert runners is self.cli.get_runners.return_value

    @mock.patch('argparse.ArgumentParser')
    def test_calls(self, ap):
        parser, runners = self.cli.build_parser()

        ap.assert_called_once_with(self.name)
        ap.return_value.add_subparsers.assert_called_once_with(
            help='Commands',
            dest='command'
        )
        self.cli.get_runners.assert_called_once_with(
            ap.return_value.add_subparsers.return_value
        )


class TestCLIGetRunners:
    def setup_method(self, method):
        self.name = 'kai',

        self.classes = (
            mock.Mock(key='somewhere'),
            mock.Mock(key='space'),
        )
        for cls in self.classes:
            cls.runner = mock.Mock()
            cls.return_value.compose.return_value = cls.key, cls.runner

        self.cli = CLI(self.name, self.classes, mock.Mock())
        self.cli.config = mock.Mock()

        self.sub = mock.Mock()

    def test_return_value(self):
        ret = self.cli.get_runners(self.sub)
        assert ret == {cls.key: cls.runner for cls in self.classes}

    def test_calls(self):
        self.cli.get_runners(self.sub)
        for cls in self.classes:
            cls.assert_called_once_with(self.cli.config)
            cls.return_value.compose.assert_called_once_with(self.sub)


class TestCLISetDebug:
    def setup_method(self, method):
        self.cli = CLI('test', (mock.Mock(),), mock.Mock())
        self.cli.log_handlers = mock.Mock(), mock.Mock(), mock.Mock()

    def test_verbose_argument_sets_debug_log_level(self):
        self.cli.args = ['--verbose', 'gospel']
        self.cli.set_debug()

        for logger in self.cli.log_handlers:
            assert logger.level == logbook.DEBUG

    def test_v_argument_sets_debug_log_level(self):
        self.cli.args = ['-v', 'undertechnical']
        self.cli.set_debug()

        for logger in self.cli.log_handlers:
            assert logger.level == logbook.DEBUG
