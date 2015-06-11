from piper import agent
from piper import api
from piper import build
from piper import config
from piper.cli.cli import CLI
from piper.db import core as db


def entry(args=None):
    classes = (
        build.BuildCLI,
        build.ExecCLI,
        agent.AgentCLI,
        api.ApiCLI,
        db.DbCLI,
    )
    cli = CLI(
        'piper',
        classes,
        config.BuildConfig,
        args=args
    )
    return cli.entry()
