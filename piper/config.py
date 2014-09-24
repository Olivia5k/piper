import os
import yaml
import logbook
import jsonschema

from piper.utils import dynamic_load


class ConfigError(Exception):
    pass


class BuildConfig(object):
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
        self.raw = None

        self.data = {}
        self.classes = {}

        self.log = logbook.Logger(self.__class__.__name__)

    def load(self):
        self.log.debug('Loading configuration')
        self.load_config()
        self.validate_config()
        self.load_classes()
        return self

    def load_config(self):
        """
        Parses the configuration file and dies in flames if there are errors.

        """

        if not os.path.isfile('piper.yml'):
            err = 'Config file not found in $PWD. Aborting.'
            self.log.error(err)
            raise ConfigError(err)

        with open('piper.yml') as config:
            file_data = config.read()

            try:
                self.raw = yaml.safe_load(file_data)

            except yaml.parser.ParserError as exc:
                self.log.error(exc)
                err = 'Invalid YAML in piper.yml. Aborting.'
                self.log.error(err)
                raise ConfigError(err)

        self.log.debug('Configuration file loaded.')

    def validate_config(self):
        self.log.debug('Validating root config...')
        jsonschema.validate(self.raw, self.schema)

    def load_classes(self):
        self.log.debug("Loading classes...")

        targets = set()

        targets.add(self.raw['version']['class'])
        targets.add(self.raw['db']['class'])

        for env in self.raw['envs'].values():
            targets.add(env['class'])

        for step in self.raw['steps'].values():
            targets.add(step['class'])

        for cls in targets:
            self.log.debug("Loading class '{0}()'".format(cls))
            self.classes[cls] = dynamic_load(cls)

        self.log.debug("Class loading done.")

    def merge_namespace(self, ns):
        """
        Take an argparse namespace and merge whatever it had directly in to the
        configuration object.

        Before this, we used to shuffle around both, to mostly the same use.

        """

        self.log.debug('Merging argparse namespace')
        for key in filter(lambda x: not x.startswith('_'), dir(ns)):
            attr = getattr(ns, key)
            setattr(self, key, attr)

    def get_database(self):
        return self.classes[self.raw['db']['class']]()
