import sys

from piper.core import Piper


def main():
    # TODO: dat argparse
    env_key = sys.argv[1]
    set_key = sys.argv[2]

    piper = Piper(env_key, set_key)
    piper.setup()
    piper.execute()
