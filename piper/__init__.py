import sys

import jsonschema
from piper.core import Piper


def main():
    # TODO: dat argparse
    env_key = sys.argv[1]
    job_key = sys.argv[2]

    piper = Piper(env_key, job_key)
    try:
        piper.setup()
        piper.execute()
        piper.teardown()
    except jsonschema.exceptions.ValidationError as e:
        print(e)
        raise
