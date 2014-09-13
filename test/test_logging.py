from piper.logging import BlessingsStringFormatter as BSF
from piper.logging import Colorizer
from piper.logging import SEPARATOR

import mock


class TestBlessingsStringFormatterColorize(object):
    def setup_method(self, method):
        self.color = 'color_code'
        self.string = 'mock'

        self.bsf = BSF()
        self.bsf.terminal = mock.Mock()
        self.bsf.terminal.color.return_value = self.color
        self.bsf.get_color = mock.Mock()

    def test_present_in_cache(self):
        self.bsf.md5_cache = mock.Mock()
        ret = self.bsf.colorize(self.string)
        assert ret is self.bsf.md5_cache.get.return_value
        assert self.bsf.terminal.color.call_count == 0

    @mock.patch('hashlib.md5')
    def test_not_present_in_cache(self, md5):
        self.bsf.md5_cache = mock.Mock()
        self.bsf.md5_cache.get.return_value = False

        ret = self.bsf.colorize(self.string)

        self.bsf.terminal.color.assert_called_once_with(
            self.bsf.get_color.return_value
        )
        self.bsf.md5_cache.update.assert_called_once_with(
            {self.string: self.color + self.string}
        )
        assert ret == self.color + self.string

    @mock.patch('hashlib.md5')
    def test_cache_population(self, md5):
        self.string = 'test'
        md5.return_value.hexdigest.return_value = 'f'
        ret1 = self.bsf.colorize(self.string)
        ret2 = self.bsf.colorize(self.string)

        assert ret1 == ret2
        assert md5.call_count == 1


class TestBlessingsStringFormatterFormatRecord(object):
    def setup_method(self, method):
        color = 'black'
        channel = 'no{0}return'.format(SEPARATOR)
        side = ['1', '2']
        ret = '1no{0}2return'.format(color + SEPARATOR)

        self.bsf = BSF()
        self.bsf.prepare_record = mock.Mock()
        self.bsf._formatter = mock.Mock()
        self.bsf.terminal = mock.Mock()
        self.bsf.terminal.color.side_effect = side
        self.bsf.terminal.black = color
        self.bsf.level_color = mock.Mock()
        self.bsf.colorized_channel = mock.Mock()

        self.record = mock.Mock()
        self.record.channel = channel
        self.handler = mock.Mock()
        self.bsf.prepare_record.return_value = self.record
        self.bsf.colorized_channel.return_value = ret

        self.kwargs = {
            'record': self.bsf.prepare_record.return_value,
            'handler': self.handler,
            't': self.bsf.terminal,
            'level_color': self.bsf.level_color.return_value,
            'colorized_channel': self.bsf.colorized_channel.return_value,
        }

    def test_proper_kwargs(self):
        self.bsf.format_record(self.record, self.handler)

        assert self.bsf._formatter.format.call_count == 1
        self.bsf._formatter.format.assert_called_once_with(**self.kwargs)


class TestBlessingsStringFormatterPrepareRecord(object):
    def setup_method(self, method):
        self.rc = mock.Mock()
        self.colorizer = mock.Mock()
        self.colorizer.colorize.return_value = True, self.rc
        self.bsf = BSF(colorizers=(self.colorizer, self.colorizer))

    def test_colorization(self):
        self.bsf.prepare_record(self.rc)
        assert self.colorizer.colorize.call_count == 2

    def test_abort(self):
        self.colorizer.aborting = True
        self.bsf.prepare_record(self.rc)
        assert self.colorizer.colorize.call_count == 1


class TestColorizerColorize(object):
    def test_stop_if_no_matches(self):
        color = Colorizer('regexp', 'replace')
        done, ret = color.colorize('message')

        assert done is False
        assert ret is 'message'

    def test_colorize(self):
        string = 'a voice in the dark'
        regexp = r'(voice in)'
        replacement = 'silent {t.bold}{0}'

        color = Colorizer(regexp, replacement)
        color.terminal = mock.Mock(bold='<bold>', normal='<normal>')

        done, ret = color.colorize(string)

        assert done is True
        assert ret == 'a silent <bold>voice in<normal> the dark'

    def test_colorize_multiple(self):
        string = 'new york, new york'
        regexp = r'(new)'
        replacement = '{t.bold}{0}'

        color = Colorizer(regexp, replacement)
        color.terminal = mock.Mock(bold='<bold>', normal='<normal>')

        done, ret = color.colorize(string)

        assert done is True
        assert ret == '<bold>new<normal> york, <bold>new<normal> york'
