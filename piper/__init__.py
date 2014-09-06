import sys

import jsonschema
from piper.core import Piper
from piper.logging import handler


def main():
    # TODO: dat argparse
    job_key = sys.argv[1]
    env_key = sys.argv[2]

    with handler.applicationbound():
        piper = Piper(job_key, env_key)
        try:
            piper.setup()
            piper.execute()
            piper.teardown()
        # TODO: Print nice error messages upon errors
        except jsonschema.exceptions.ValidationError as e:  # pragma: nocover
            print(e)
            raise
