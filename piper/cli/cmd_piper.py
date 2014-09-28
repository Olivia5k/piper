from piper import build
from piper.cli.cli import CLIBase
from piper.db import core as db


def entry(args=None):
    cli = CLIBase('piper', (build.ExecCLI, db.DbCLI), args=args)
    return cli.entry()
