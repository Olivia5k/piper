import piper
import logbook

import mock


class TestBuild(object):
    @mock.patch('piper.Build')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, Build):
        piper.main()

        assert Build.call_count == 1
        Build.return_value.run.assert_called_once_with()

    @mock.patch('piper.Build')
    @mock.patch('piper.build_parser')
    @mock.patch('piper.get_handler')
    def test_debug_argument_sets_debug_log_level(self, gh, bp, Build):
        bp.return_value.parse_args.return_value.debug = True
        piper.main()

        assert Build.call_count == 1
        assert gh.return_value.level == logbook.DEBUG
        Build.return_value.run.assert_called_once_with()
