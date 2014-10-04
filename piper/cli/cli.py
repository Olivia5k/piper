import sys
import argparse
import logbook

from piper import logging


class CLIBase(object):
    """
    Semi-abstract class that sets up a argparse namespace and executes
    commands from pluggable CLI classes.

    """

    def __init__(self, name, classes, config_class, args=()):
        self.name = name
        self.classes = classes
        self.config_class = config_class
        self.args = args

        if not self.args:
            self.args = sys.argv[1:]

        self.config = None
        self.log_handlers = None

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
        debug = False
        if '-v' in self.args or '--verbose' in self.args:
            debug = True

        self.log_handlers = logging.get_handlers(debug)

    def load_config(self):  # pragma: nocover
        self.config = self.config_class().load()

    def set_debug(self):
        # Lower the logging level if we're being verbose.
        if '-v' in self.args or '--verbose' in self.args:
            for handler in self.log_handlers:
                handler.level = logbook.DEBUG

    def entry(self):
        self.get_handlers()

        for handler in self.log_handlers:
            handler.push_application()

        self.set_debug()
        self.load_config()

        parser, runners = self.build_parser()
        ns = parser.parse_args(self.args)
        self.config.merge_namespace(ns)

        # Just running the command should print the help.
        if not self.config.command:
            parser.print_help()
            return 0

        # Actually execute the command
        exitcode = runners[self.config.command]()

        return exitcode
