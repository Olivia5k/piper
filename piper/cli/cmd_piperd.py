from piper.api import api
from piper.cli.cli import CLIBase


def entry(args=None):
    cli = CLIBase('piperd', (api.ApiCLI,), args=args)
    return cli.entry()
