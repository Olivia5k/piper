from piper import build
from piper.cli.cli import CLIBase
from piper.db import core as db


def entry():
    cli = CLIBase('piper', (build.ExecCLI, db.DbCLI))
    return cli.entry()
