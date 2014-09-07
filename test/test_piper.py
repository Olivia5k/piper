import piper

import mock


class TestPiper(object):
    @mock.patch('piper.Piper')
    @mock.patch('sys.argv')
    def test_main_entry_point(self, argv, Piper):
        piper.main()

        assert Piper.call_count == 1
        Piper.return_value.run.assert_called_once_with()
