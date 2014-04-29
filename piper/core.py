import sys
import os

import yaml
import logbook

from piper.utils import DotDict


class Piper(object):
    """
    The main pipeline runner.

    This class loads the configurations, sets up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    The functions are almost executed in the order found in this file. Woo!

    """

    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'version': {
                'description': 'Semantic version string for this config.',
                'type': 'string',
            },
            'environment': {
                'description': 'The environment configuration for this build.',
                'type': 'object',
            },
            'steps': {
                'description': 'Definitions of executable build steps.',
                'type': 'array',
            },
            'sets': {
                'description': 'Runnable collections of steps.',
                'type': 'object',
                'additionalProperties': True,
            },
        },
    }

    def __init__(self):
        self.raw_config = None  # Dict data
        self.config = None  # DotDict object

        self.log = logbook.Logger(self.__class__.__name__)

    def setup(self):
        """
        Performs all setup steps

        This is basically an umbrella function that runs setup for all the
        things that the class needs to run a fully configured execute().

        """

        self.load_config()

    def load_config(self):
        """
        Parses the configuration file and dies in flames if there are errors.

        """

        if not os.path.isfile('piper.yml'):
            self.log.error('Config file not found in $PWD. Aborting.')
            return sys.exit(127)  # 'return' is for the tests to make sense

        with open('piper.yml') as config:
            file_data = config.read()

            try:
                self.raw_config = yaml.safe_load(file_data)

            except yaml.parser.ParserError as exc:
                self.log.error(exc)
                self.log.error('Invalid YAML in piper.yml. Aborting.')
                return sys.exit(126)

        self.config = DotDict(self.raw_config)
        self.log.info('Configuration file loaded.')

    def setup_environment(self):
        """
        Load the environment and it's configuration

        """

        pass

    def setup_steps(self):
        """
        Loads the steps and their configuration.

        Also determines which collection of steps is to be ran.

        """

        pass

    def execute(self):
        """
        Runs the steps and determines whether to continue or not.

        Of all the things to happen in this application, this is probably
        the most important part!

        """

        pass

    def save_state(self):
        """
        Collects all data about the pipeline being built and persists it.

        """

        pass

    def teardown_environment(self):
        """
        Execute teardown step of the environment

        """

        pass
