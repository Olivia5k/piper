from piper.cli.cmd_piper import piper_entry
import logbook

import mock


# TODO: These could have some refactoring love, but I've yet to find a nice way
# to do setup on mock.patch objects without passing them around like krazy.
class TestPiperEntry(object):
    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.config.BuildConfig')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, gh, BC, bp):
        # Fake log handlers, needs to be macic mocks due to context managing
        gh.return_value = mock.MagicMock(), mock.MagicMock()

        parser, runners = mock.MagicMock(), mock.MagicMock()
        bp.return_value = (parser, runners)

        ns = parser.parse_args.return_value
        conf = BC.return_value.load.return_value
        runners[ns.command].return_value = 0

        ret = piper_entry()

        assert ret == 0
        BC.return_value.load.assert_called_once_with()
        runners[ns.command].assert_called_once_with(ns, conf)

    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('sys.argv')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    def test_failing_build_exits_nonzero(self, gh, argv, bp):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        parser, runners = mock.MagicMock(), mock.MagicMock()
        bp.return_value = (parser, runners)

        ns = parser.parse_args.return_value
        runners[ns.command].return_value = 1

        ret = piper_entry()
        assert ret == 1

    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    def test_verbose_argument_sets_debug_log_level(self, gh, bp):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        parser, runners = mock.MagicMock(), mock.MagicMock()
        bp.return_value = (parser, runners)

        ns = parser.parse_args.return_value
        ns.verbose = True
        piper_entry()

        for logger in gh.return_value:
            assert logger.level == logbook.DEBUG

    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    def test_no_command_runs_help(self, gh, bp):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        parser, runners = mock.MagicMock(), mock.MagicMock()
        bp.return_value = (parser, runners)

        ns = parser.parse_args.return_value
        ns.command = False
        ret = piper_entry()

        assert ret == 0
        parser.print_help.assert_called_once_with()
