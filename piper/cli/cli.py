import sys
import argparse
import logbook

from piper import config
from piper import logging


class CLIBase(object):
    """
    Semi-abstract class that sets up a argparse namespace and executes
    commands from pluggable CLI classes.

    """

    def __init__(self, name, classes):
        self.name = name
        self.classes = classes

    def build_parser(self):
        # Create the root parser
        parser = argparse.ArgumentParser(self.name)
        self.global_arguments(parser)

        # Set up a base subparser
        sub = parser.add_subparsers(help="Commands", dest="command")

        # Instantiate the CLIs with the config, and construct the dict of
        # runner entry points.
        runners = self.get_runners(sub)

        return parser, runners

    def global_arguments(self, parser):  # pragma: nocover
        parser.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Enable debugging output',
        )

    def get_runners(self, sub):
        return dict(cli(self.config).compose(sub) for cli in self.classes)

    def get_handlers(self):  # pragma: nocover
        return logging.get_handlers()

    def load_config(self):  # pragma: nocover
        self.config = config.BuildConfig().load()

    def entry(self):
        stream, logfile = self.get_handlers()

        with stream.applicationbound():
            with logfile.applicationbound():
                self.load_config()

                parser, runners = self.build_parser()
                ns = parser.parse_args(sys.argv[1:])
                self.config.merge_namespace(ns)

                # Just running the command should print the help.
                if not self.config.command:
                    parser.print_help()
                    return 0

                # Lower the logging level if we're being verbose.
                if self.config.verbose is True:
                    stream.level = logbook.DEBUG
                    logfile.level = logbook.DEBUG

                # Actually execute the command
                exitcode = runners[self.config.command]()
                return exitcode
