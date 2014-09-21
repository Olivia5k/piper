from piper.api import api
from piper.cli.cli import CLIBase


def entry():
    cli = CLIBase('piperd', (api.ApiCLI,))
    return cli.entry()
