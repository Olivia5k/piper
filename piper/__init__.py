import sys

import jsonschema
from piper.core import Piper
from piper.logging import handler


def main():
    # TODO: dat argparse
    env_key = sys.argv[1]
    job_key = sys.argv[2]

    with handler.applicationbound():
        piper = Piper(env_key, job_key)
        try:
            piper.setup()
            piper.execute()
            piper.teardown()
        except jsonschema.exceptions.ValidationError as e:
            print(e)
            raise
