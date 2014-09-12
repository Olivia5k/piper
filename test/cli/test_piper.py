from piper.cli.piper import piper_entry
import logbook

import mock


class TestPiperEntry(object):
    @mock.patch('piper.cli.piper.Build')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, Build):
        piper_entry()

        assert Build.call_count == 1
        Build.return_value.run.assert_called_once_with()

    @mock.patch('piper.cli.piper.Build')
    @mock.patch('piper.cli.piper.build_parser')
    @mock.patch('piper.cli.piper.get_handler')
    def test_debug_argument_sets_debug_log_level(self, gh, bp, Build):
        bp.return_value.parse_args.return_value.debug = True
        piper_entry()

        assert Build.call_count == 1
        assert gh.return_value.level == logbook.DEBUG
        Build.return_value.run.assert_called_once_with()
