from piper.logging import BlessingsStringFormatter as BSF
import mock


class TestBlessingsStringFormatterChannelColor(object):
    def setup_method(self, method):
        self.bsf = BSF()
        self.bsf.terminal = mock.Mock()
        self.bsf.get_color = mock.Mock()
        self.rc = mock.Mock()

    def test_present_in_cache(self):
        self.bsf.md5_cache = mock.Mock()
        ret = self.bsf.channel_color(self.rc)
        assert ret is self.bsf.md5_cache.get.return_value
        assert self.bsf.terminal.color.call_count == 0

    @mock.patch('hashlib.md5')
    def test_not_present_in_cache(self, md5):
        self.bsf.md5_cache = mock.Mock()
        self.bsf.md5_cache.get.return_value = False
        color = self.bsf.terminal.color.return_value

        ret = self.bsf.channel_color(self.rc)

        self.bsf.terminal.color.assert_called_once_with(
            self.bsf.get_color.return_value
        )
        self.bsf.md5_cache.update.assert_called_once_with(
            {self.rc.channel: color}
        )
        assert ret is color

    @mock.patch('hashlib.md5')
    def test_cache_population(self, md5):
        self.rc.channel = 'test'
        md5.return_value.hexdigest.return_value = 'f'
        ret1 = self.bsf.channel_color(self.rc)
        ret2 = self.bsf.channel_color(self.rc)

        assert ret1 == ret2
        assert md5.call_count == 1


class TestBlessingsStringFormatterFormatRecord(object):
    def setup_method(self, method):
        self.bsf = BSF()
        self.bsf.prepare_record = mock.Mock()
        self.bsf._formatter = mock.Mock()
        self.bsf.terminal = mock.Mock()
        self.bsf.level_color = mock.Mock()
        self.bsf.channel_color = mock.Mock()

        self.record = mock.Mock()
        self.handler = mock.Mock()

        self.kwargs = {
            'record': self.bsf.prepare_record.return_value,
            'handler': self.handler,
            't': self.bsf.terminal,
            'level_color': self.bsf.level_color.return_value,
            'channel_color': self.bsf.channel_color.return_value,
        }

    def test_proper_kwargs(self):
        self.bsf.format_record(self.record, self.handler)

        assert self.bsf._formatter.format.call_count == 1
        self.bsf._formatter.format.assert_called_once_with(**self.kwargs)
