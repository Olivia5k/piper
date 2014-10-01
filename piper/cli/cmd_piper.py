from piper import build
from piper.cli.cli import CLIBase


def entry(args=None):
    cli = CLIBase('piper', (build.ExecCLI,), args=args)
    return cli.entry()
