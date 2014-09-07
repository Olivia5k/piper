import sys
import os

import yaml
import logbook
import jsonschema
import six

from piper.utils import DotDict
from piper.utils import dynamic_load


class Piper(object):
    """
    The main pipeline runner.

    This class loads the configurations, jobs up all other components,
    executes them in whatever order they are supposed to happen in, collects
    data about the state of the pipeline and persists it, and finally tears
    down the components that needs tearing down.

    """

    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        'type': 'object',
        'additionalProperties': False,
        'required': ['version', 'envs', 'steps', 'jobs'],
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
            'jobs': {
                'description': 'Runnable collections of steps.',
                'type': 'object',
                'additionalProperties': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
            },
        },
    }

    def __init__(self, ns):
        self.ns = ns
        self.job_key = self.ns.job
        self.env_key = self.ns.env

        self.raw_config = None  # Dict data
        self.config = None  # DotDict object

        self.classes = {}
        self.steps = {}
        self.order = []
        self.success = None

        self.log = logbook.Logger(self.__class__.__name__)

    def run(self):
        """
        Main entry point

        This is run when starting the script from the command line.

        """

        self.setup()
        self.execute()
        self.teardown()

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
        self.configure_job()

        self.setup_env()

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

        self.env = cls(self.ns, env_config)
        self.log.debug('Validating env config...')
        self.env.validate()
        self.env.log.info('Environment configured.')

    def configure_steps(self):
        """
        Configures the steps according to their config sections.

        """

        for step_key, step_config in self.config.steps.items():
            cls = self.classes[step_config['class']]

            step = cls(step_key, step_config)
            step.log.debug('Validating config...')
            step.validate()
            step.log.info('Step configured.')
            self.steps[step_key] = step

    def configure_job(self):
        """
        Places steps in proper order according to the chosen set.

        """

        for step_key in self.config.jobs[self.job_key]:
            step = self.steps[step_key]
            self.order.append(step)

            if step.config.depends:
                self.inject_step_dependency(step, step.config.depends)

        self.log.info('Set order configured.')
        self.log.debug(str(self.order))

    def inject_step_dependency(self, step, depends):
        # We can pass both lists and strings. Handle accordingly.
        if isinstance(depends, six.string_types):
            targets = (depends,)
        else:
            targets = depends

        index = self.order.index(step)
        for dep_key in targets:
            dep = self.steps[dep_key]

            self.order.insert(index, dep)
            index += 1  # So that the next one gets the right order

            self.log.info("Added dependency step '{0}' for '{1}'".format(
                dep.key, step.key
            ))

            # If the injected step has dependencies as well, we need to
            # recursively add those too.
            if dep.config.depends:
                self.inject_step_dependency(dep, dep.config.depends)

    def setup_env(self):
        """
        Execute setup steps of the env

        """

        self.env.log.info('Setting up env...')
        self.env.setup()

    def execute(self):
        """
        Runs the steps and determines whether to continue or not.

        Of all the things to happen in this application, this is probably
        the most important part!

        """

        total = len(self.order)
        self.log.info('Running complete "{0}" set...'.format(self.job_key))

        for x, step in enumerate(self.order, start=1):
            step.set_index(x, total)
            step.log.info('Running...')
            proc = self.env.execute(step)

            if proc.success:
                step.log.info('Step complete.')
            else:
                # If the success is not positive, bail and stop running.
                step.log.error('Step "{0}" failed.'.format(self.job_key))
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

    def teardown(self):
        self.teardown_env()

    def teardown_env(self):
        """
        Execute teardown step of the env

        """

        self.env.log.info('Tearing down env...')
        self.env.teardown()
