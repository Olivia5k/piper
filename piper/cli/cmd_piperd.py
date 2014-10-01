from piper.api import api
from piper.db import core as db
from piper.cli.cli import CLIBase


def entry(args=None):
    cli = CLIBase('piperd', (api.ApiCLI, db.DbCLI), args=args)
    return cli.entry()
