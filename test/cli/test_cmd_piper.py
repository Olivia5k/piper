from piper.cli.cmd_piper import piper_entry
import logbook

import mock


class TestPiperEntry(object):
    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('piper.cli.cmd_piper.BuildConfig')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, BC, B, bp):
        piper_entry()

        B.assert_called_once_with(
            bp.return_value.parse_args.return_value,
            BC.return_value.load.return_value,
        )
        B.return_value.run.assert_called_once_with()

    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('sys.argv')
    @mock.patch('sys.exit')
    def test_failing_build_exits_nonzero(self, exit, argv, Build):
        Build.return_value.run.return_value = False
        piper_entry()

        Build.return_value.run.assert_called_once_with()
        exit.assert_called_once_with(1)

    @mock.patch('piper.cli.cmd_piper.Build')
    @mock.patch('piper.cli.cmd_piper.build_parser')
    @mock.patch('piper.cli.cmd_piper.get_handler')
    def test_debug_argument_sets_debug_log_level(self, gh, bp, Build):
        bp.return_value.parse_args.return_value.debug = True
        piper_entry()

        assert gh.return_value.level == logbook.DEBUG
        Build.return_value.run.assert_called_once_with()
