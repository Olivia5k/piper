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

DEFAULT_FORMAT_STRING = (
    '{t.bold}{t.black}['
    '{t.cyan}{record.time:%Y-%m-%d %H:%M:%S.%f}'
    '{t.black}]{t.normal} '
    '{level_color}{record.level_name:>5} '
    '{t.bold}{channel_color}{record.channel}'
    '{t.bold}{t.black}:{t.normal} '
    '{record.message}'
)


class BlessingsStringFormatter(logbook.StringFormatter):
    """
    StringFormatter subclass that gives access to blessings.Terminal().

    This class adds the `t` object in the formatting string, which is an
    instance of blessings.Terminal(). It also provides helper functions to
    colorize the log level and log channel.

    """

    terminal = blessings.Terminal()
    md5_cache = {}

    def __init__(self, format_string=None):
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
            'channel_color': self.channel_color(record),
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

    def level_color(self, rc):
        ret = ''
        if rc.level_name in ('ERROR', 'CRITICAL'):
            ret = self.terminal.red + self.terminal.bold
        if rc.level_name == 'WARNING':
            ret = self.terminal.yellow + self.terminal.bold
        if rc.level_name == 'DEBUG':
            ret = self.terminal.white
        return ret

    def channel_color(self, rc):
        """
        Colorize the logging channel, providing visual cues to where the
        message is from.

        a color in the terminal colorspace is selected based on the integer
        value of md5sum of the channel name. Once calculated it is cached so
        that the digestion only happens once per channel name.

        """

        color = self.md5_cache.get(rc.channel)
        if not color:
            md5 = hashlib.md5(rc.channel.encode()).hexdigest()
            index = self.get_color(md5)
            color = self.terminal.color(index)
            self.md5_cache.update({rc.channel: color})

        return color

    def get_color(self, md5):  # pragma: nocover
        return COLORS[int(md5, 16) % COLOR_LEN]

    def prepare_record(self, rc):
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


handler = logbook.StreamHandler(sys.stdout)
handler.formatter = BlessingsStringFormatter()
