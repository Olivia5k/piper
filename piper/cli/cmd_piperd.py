from piper import agent
from piper import api
from piper import config
from piper.cli.cli import CLI
from piper.db import core as db


def entry(args=None):
    classes = (
        api.ApiCLI,
        db.DbCLI,
        agent.AgentCLI,
    )
    cli = CLI('piperd', classes, config.AgentConfig, args=args)
    return cli.entry()
