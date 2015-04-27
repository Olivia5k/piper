from piper.api import api
from piper.api import api
from piper.db import core as db
from piper import prop
from piper import config
from piper.cli.cli import CLI


def entry(args=None):
    classes = (
        api.ApiCLI,
        db.DbCLI,
        prop.PropCLI,
    )
    cli = CLI('piperd', classes, config.AgentConfig, args=args)
    return cli.entry()
