import sys
import os

import yaml
import logbook
import jsonschema

from piper.utils import DotDict
from piper.utils import dynamic_load


class Piper(object):
    """
    The main pipeline runner.

    This class loads the configurations, sets up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    """

    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        'type': 'object',
        'additionalProperties': False,
        'required': ['version', 'envs', 'steps', 'sets'],
        'properties': {
            'version': {
                'description': 'Semantic version string for this config.',
                'type': 'string',
            },
            'envs': {
                'description': 'The env configuration for this build.',
                'type': 'object',
                'additionalProperties': {
                    'type': 'object',
                },
            },
            'steps': {
                'description': 'Definitions of executable build steps.',
                'type': 'object',
            },
            'sets': {
                'description': 'Runnable collections of steps.',
                'type': 'object',
                'additionalProperties': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
            },
        },
    }

    def __init__(self, env_key, set_key):
        self.env_key = env_key
        self.set_key = set_key

        self.raw_config = None  # Dict data
        self.config = None  # DotDict object

        self.classes = {}
        self.steps = {}
        self.order = []
        self.success = None

        self.log = logbook.Logger(self.__class__.__name__)

    def setup(self):
        """
        Performs all setup steps

        This is basically an umbrella function that runs setup for all the
        things that the class needs to run a fully configured execute().

        """

        self.load_config()
        self.validate_config()
        self.load_classes()

        self.configure_env()
        self.configure_steps()
        self.configure_set()

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

    def validate_config(self):
        self.log.info('Validating root config...')
        jsonschema.validate(self.config.data, self.schema)

    def load_classes(self):
        self.log.info("Loading classes for steps and envs...")

        classes = set()
        for env in self.config.envs.values():
            classes.add(env['class'])

        for step in self.config.steps.values():
            classes.add(step['class'])

        for cls in classes:
            self.log.debug("Loading class '{0}()'".format(cls))
            self.classes[cls] = dynamic_load(cls)

        self.log.info("Class loading done.")

    def configure_env(self):
        """
        Configures the environment according to its config file.

        """

        self.log.info('Loading environment...')
        env_config = self.config.envs[self.env_key]
        cls = self.classes[env_config['class']]

        self.env = cls(env_config)
        self.log.debug('Validating env config...')
        self.env.validate()
        self.env.log.info('Environment configured.')

    def configure_steps(self):
        """
        Configures the steps according to their config sections.

        """

        for step_key, step_config in self.config.steps.items():
            cls = self.classes[step_config['class']]

            step = cls(step_config)
            step.log.debug('Validating config...')
            step.validate()
            step.log.info('Step configured.')
            self.steps[step_key] = step

    def configure_set(self):
        """
        Places steps in proper order according to the chosen set.

        """

        for step_key in self.config.sets[self.set_key]:
            self.order.append(self.steps[step_key])

        self.log.info('Set order configured.')

    def execute(self):
        """
        Runs the steps and determines whether to continue or not.

        Of all the things to happen in this application, this is probably
        the most important part!

        """

        self.log.info('Running complete "{0}" set...'.format(self.set_key))
        for step in self.order:
            step.log.info('Running...')
            step.execute()

            # If the success is not positive, bail and stop running.
            if not step.success:
                step.log.error('Step "{0}" failed.'.format(self.set_key))
                self.success = False
                break

        # As long as we did not break out of the loop above, the build is
        # to be deemed succesful.
        if self.success is not False:
            self.success = True

    def save_state(self):
        """
        Collects all data about the pipeline being built and persists it.

        """

        pass

    def teardown_env(self):
        """
        Execute teardown step of the env

        """

        pass
