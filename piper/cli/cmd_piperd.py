import sys
import argparse
import logbook

from piper.api import core as api
from piper import config
from piper.logging import get_handlers


def build_parser(conf):  # pragma: nocover
    parser = argparse.ArgumentParser('piperd')

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Enable debugging output',
    )

    subparsers = parser.add_subparsers(help="Core commands", dest="command")

    clis = (
        api.ApiCLI(conf),
    )

    runners = dict(c.compose(subparsers) for c in clis)

    return parser, runners


def piperd_entry():
    stream, logfile = get_handlers()

    with stream.applicationbound():
        with logfile.applicationbound():
            conf = config.BuildConfig().load()
            parser, runners = build_parser(conf)
            ns = parser.parse_args(sys.argv[1:])

            # Just running 'piperd' should print the help.
            if not ns.command:
                parser.print_help()
                return 0

            # Lower the logging level if we're being verbose.
            if ns.verbose is True:
                stream.level = logbook.DEBUG
                logfile.level = logbook.DEBUG

            # Actually execute the command
            exitcode = runners[ns.command](ns)
            return exitcode
