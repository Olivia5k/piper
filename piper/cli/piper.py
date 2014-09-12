import sys
import argparse
import logbook

from piper.build import Build
from piper.config import BuildConfig
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


def piper_entry():
    handler = get_handler()

    with handler.applicationbound():
        parser = build_parser()
        ns = parser.parse_args(sys.argv[1:])

        if ns.debug is True:
            handler.level = logbook.DEBUG

        config = BuildConfig(ns).load()

        success = Build(ns, config).run()
        if not success:
            sys.exit(1)
