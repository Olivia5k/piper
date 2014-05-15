import sys

import jsonschema
from piper.core import Piper


def main():
    # TODO: dat argparse
    env_key = sys.argv[1]
    set_key = sys.argv[2]

    piper = Piper(env_key, set_key)
    try:
        piper.setup()
        piper.execute()
    except jsonschema.exceptions.ValidationError as e:
        print(e)
        raise
