import os
import sys
import yaml
import logbook
import jsonschema

from piper.utils import DotDict
from piper.utils import dynamic_load


class BuildConfig(DotDict):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        'type': 'object',
        'additionalProperties': False,
        'required': ['version', 'envs', 'steps', 'jobs'],
        'properties': {
            'version': {
                'description':
                    'Versioning setup for this project. This sets up what '
                    'commands to run to determine the version of the job '
                    'being executed',
                'type': 'object',
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
            'db': {
                'description': 'Database configuration',
                'type': 'object',
                'required': ['host'],
                'properties': {
                    'host': {
                        'description': 'The host to connect to',
                        'type': 'string',
                    },
                    'user': {
                        'description': 'The username used for authentication',
                        'type': ['string', 'null'],
                    },
                    'password': {
                        'description': 'The passord used for authentication',
                        'type': ['string', 'null'],
                    },
                },
            },
        },
    }

    def __init__(self):
        self.raw_config = None

        self.data = {}
        self.classes = {}

        self.log = logbook.Logger(self.__class__.__name__)

    def load(self):
        self.log.info('Loading configuration')
        self.load_config()
        self.validate_config()
        self.load_classes()
        return self

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

        self.data = self.raw_config
        self.log.debug('Configuration file loaded.')

    def validate_config(self):
        self.log.debug('Validating root config...')
        jsonschema.validate(self.raw_config, self.schema)

    def load_classes(self):
        self.log.debug("Loading classes...")

        targets = set()

        targets.add(self.version['class'])
        targets.add(self.db['class'])

        for env in self.envs.values():
            targets.add(env['class'])

        for step in self.steps.values():
            targets.add(step['class'])

        for cls in targets:
            self.log.debug("Loading class '{0}()'".format(cls))
            self.classes[cls] = dynamic_load(cls)

        self.log.debug("Class loading done.")

    def get_database(self):
        return self.classes[self.db['class']]()
