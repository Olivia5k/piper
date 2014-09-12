#!/usr/bin/env python
# coding: utf-8

import re
import sys
import hashlib
import logbook
import blessings

# TODO: Some of these only work on dark terminals. Investigate.
COLORS = (
    23, 24, 25, 26, 27, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 41, 42, 43, 44,
    45, 47, 48, 49, 50, 51, 58, 59, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
    74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 94, 95, 96, 97,
    98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112,
    113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 130, 131, 132, 133,
    134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148,
    149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 162, 166, 167, 168,
    169, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184,
    185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 202, 205, 206, 207,
    208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222,
    223, 224, 225, 226, 227, 228
)
COLOR_LEN = len(COLORS)

# Any consecutive string containing a slash
PATH_RXP = re.compile(r'(\S*/[\S/]+)')
# The end of "foo (x/y)"
COUNTER_RXP = re.compile(r'(\s*\(\d+/\d+\))$')

DEFAULT_FORMAT_STRING = (
    '{t.bold}{t.black}['
    '{t.normal}{t.cyan}{record.time:%Y-%m-%d %H:%M:%S.%f}'
    '{t.bold}{t.black}]{t.normal} '
    '{level_color}{record.level_name:>5} '
    '{t.bold}{colorized_channel}'
    '{t.bold}{t.black}:{t.normal} '
    '{record.message}'
)

# This separator is used to split multiple channels to colorize each one.
# Dot was used at first, but that breaks command lines more than not.
SEPARATOR = ': '


class BlessingsStringFormatter(logbook.StringFormatter):
    """
    StringFormatter subclass that gives access to blessings.Terminal().

    This class adds the `t` object in the formatting string, which is an
    instance of blessings.Terminal(). It also provides helper functions to
    colorize the log level and log channel.

    """

    def __init__(self, format_string=None):
        self.terminal = blessings.Terminal()
        self.md5_cache = {}

        if not format_string:
            format_string = DEFAULT_FORMAT_STRING

        format_string += '{t.normal}'
        super(BlessingsStringFormatter, self).__init__(format_string)

    def format_record(self, record, handler):
        record = self.prepare_record(record)
        kwargs = {
            'record': record,
            'handler': handler,
            't': self.terminal,
            'level_color': self.level_color(record),
            'colorized_channel': self.colorize_channel(record.channel),
        }

        try:
            return self._formatter.format(**kwargs)

        # These handlers are tested as a part of logbook, so let's not muck
        # around in trying to simulate those errors.
        except UnicodeEncodeError:  # pragma: nocover
            # self._formatter is a str, but some of the record items
            # are unicode
            fmt = self._formatter.decode('ascii', 'replace')
            return fmt.format(**kwargs)
        except UnicodeDecodeError:  # pragma: nocover
            # self._formatter is unicode, but some of the record items
            # are non-ascii str
            fmt = self._formatter.encode('ascii', 'replace')
            return fmt.format(**kwargs)

    def level_color(self, rc):  # pragma: nocover
        ret = ''
        if rc.level_name in ('ERROR', 'CRITICAL'):
            ret = self.terminal.red + self.terminal.bold
        if rc.level_name == 'WARNING':
            ret = self.terminal.yellow + self.terminal.bold
        if rc.level_name == 'DEBUG':
            ret = self.terminal.white
        return ret

    def colorize_channel(self, channel):
        # Split the channel on the seprator and colorize each one differently
        sep = self.terminal.black + SEPARATOR
        return sep.join(map(self.colorize, channel.split(SEPARATOR)))

    def colorize(self, string):
        """
        Colorize a string based on its hash.

        a color in the terminal colorspace is selected based on the integer
        value of md5sum of the channel name. Once calculated it is cached so
        that the digestion only happens once.

        """

        colorized = self.md5_cache.get(string)
        if not colorized:
            # Don't use the ' (x/y)' part when calculating colors. This makes
            # sure that the 'foo' step is always in one color regardless if it
            # is (1/12) or (33/100).
            target = COUNTER_RXP.sub('', string)

            md5 = hashlib.md5(target.encode()).hexdigest()
            index = self.get_color(md5)
            colorized = self.terminal.color(index) + string
            self.md5_cache.update({string: colorized})

        return colorized

    def get_color(self, md5):  # pragma: nocover
        return COLORS[int(md5, 16) % COLOR_LEN]

    def prepare_record(self, rc):  # pragma: nocover
        """
        Manipulate the log message

        """

        # Colorize paths
        match = PATH_RXP.findall(rc.message)
        if match:
            for path in match:
                rc.message = rc.message.replace(
                    path,
                    self.terminal.bold + self.terminal.blue + path +
                    self.terminal.normal
                )

        return rc


def get_handler():
    try:
        # Remove the default logbook.StderrHandler so that we can actually hide
        # debug output when debug is False. If we don't remove it, it will
        # always print to stderr anyway.
        logbook.default_handler.pop_application()
    except AssertionError:
        # Also, this can die during tests because the handler does not seem to
        # be set when running them.
        pass

    handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO)
    handler.formatter = BlessingsStringFormatter()
    return handler
