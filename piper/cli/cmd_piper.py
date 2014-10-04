from piper import build
from piper import config
from piper.cli.cli import CLIBase


def entry(args=None):
    cli = CLIBase('piper', (build.ExecCLI,), config.BuildConfig, args=args)
    return cli.entry()
