import sys
import os

import yaml
import logbook


class Piper(object):
    """
    The main pipeline runner.

    This class loads the configurations, sets up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    The functions are almost executed in the order found in this file. Woo!

    """

    def __init__(self):
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
            self.raw_config = yaml.safe_load(config)
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
