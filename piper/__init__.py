import sys
import argparse
import logbook

from piper.build import Build
from piper.logging import get_handler


def build_parser():
    parser = argparse.ArgumentParser('piper')

    parser.add_argument(
        'job',
        nargs='?',
        default='build',
        help='The job to execute',
    )

    parser.add_argument(
        'env',
        nargs='?',
        default='local',
        help='The environment to execute in',
    )

    parser.add_argument(
        '--dry-run',
        '-n',
        action='store_true',
        help="Only print execution commands, don't actually do anything",
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debugging output',
    )

    return parser


def main():
    try:
        # Remove the default logbook.StderrHandler so that we can actually hide
        # debug output when debug is False. If we don't remove it, it will
        # always print to stderr anyway.
        logbook.default_handler.pop_application()
    except AssertionError:
        # Also, this can die during tests because the handler does not seem to
        # be set when running them.
        pass

    handler = get_handler()
    with handler.applicationbound():
        parser = build_parser()
        ns = parser.parse_args(sys.argv[1:])

        if ns.debug is True:
            handler.level = logbook.DEBUG

        Build(ns).run()
