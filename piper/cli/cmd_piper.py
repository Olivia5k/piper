import sys
import argparse
import logbook

from piper import db
from piper import build
from piper import config
from piper.logging import get_handlers


def build_parser():  # pragma: nocover
    parser = argparse.ArgumentParser('piper')

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Enable debugging output',
    )

    subparsers = parser.add_subparsers(help="Core commands", dest="command")

    clis = (
        build.ExecCLI(),
        db.DbCLI(),
    )

    runners = dict(c.compose(subparsers) for c in clis)

    return parser, runners


def piper_entry():
    stream, logfile = get_handlers()

    with stream.applicationbound():
        with logfile.applicationbound():
            conf = config.BuildConfig().load()
            parser, runners = build_parser(conf)
            ns = parser.parse_args(sys.argv[1:])

            # Just running 'piper' should print the help.
            if not ns.command:
                parser.print_help()
                return 0

            # Lower the logging level if we're being verbose.
            if ns.verbose is True:
                stream.level = logbook.DEBUG
                logfile.level = logbook.DEBUG

            # Actually execute the command
            exitcode = runners[ns.command](ns, conf)
            return exitcode
