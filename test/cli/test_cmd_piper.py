from piper.cli.cmd_piper import piper_entry
import logbook

import mock


class TestPiperEntry(object):
    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('piper.cli.cmd_piper.BuildConfig')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, gh, BC, B, bp):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        piper_entry()

        B.assert_called_once_with(
            bp.return_value.parse_args.return_value,
            BC.return_value.load.return_value,
        )
        B.return_value.run.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('sys.argv')
    @mock.patch('sys.exit')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    def test_failing_build_exits_nonzero(self, gh, exit, argv, Build):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        Build.return_value.run.return_value = False
        piper_entry()

        Build.return_value.run.assert_called_once_with()
        exit.assert_called_once_with(1)

    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.get_handlers')
    def test_debug_argument_sets_debug_log_level(self, gh, bp, Build):
        gh.return_value = mock.MagicMock(), mock.MagicMock()
        bp.return_value.parse_args.return_value.debug = True
        piper_entry()

        for logger in gh.return_value:
            assert logger.level == logbook.DEBUG
        Build.return_value.run.assert_called_once_with()
