import sys
import argparse

from piper.core import Piper
from piper.logging import handler


def build_parser():
    parser = argparse.ArgumentParser('piper')

    parser.add_argument(
        'job',
        nargs='?',
        default='build',
        help='The job to execute',
    )

    parser.add_argument(
        'env',
        nargs='?',
        default='local',
        help='The environment to execute in'
    )

    return parser


def main():
    with handler.applicationbound():
        parser = build_parser()
        ns = parser.parse_args(sys.argv[1:])

        piper = Piper(ns.job, ns.env)
        piper.setup()
        piper.execute()
        piper.teardown()
