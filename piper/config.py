import os
import yaml
import logbook
import jsonschema

from piper.utils import dynamic_load


DB_SCHEMA = {
    'description': 'Database configuration',
    'type': 'object',
    'required': ['class', 'host'],
    'properties': {
        'class': {
            'description': 'The piper.db class to use as DB abstraction',
            'type': 'string',
        },
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
}


class ConfigError(Exception):
    pass


class Config(object):
    def __init__(self, filename=None, raw=None):
        args = (filename, raw)
        assert any(args), 'Need to specify `filename` or `raw`'
        assert not all(args), 'Cannot specify both ' + \
            '`filename` and `raw` at the same time'

        self.filename = filename
        self.raw = raw

        self.classes = {}

        self.log = logbook.Logger(self.__class__.__name__)

    def load(self):
        self.log.debug('Loading configuration')

        if self.filename:
            self.load_config()
        else:
            self.log.debug('Using provided raw configuration.')

        self.validate_config()
        self.load_classes()
        return self

    def load_config(self):
        """
        Parses the configuration file and dies in flames if there are errors.

        """

        if not os.path.isfile(self.filename):
            err = 'Config file not found in $PWD. Aborting.'
            self.log.error(err)
            raise ConfigError(err)

        with open(self.filename) as config:
            file_data = config.read()

            try:
                self.raw = yaml.safe_load(file_data)

            except yaml.parser.ParserError as exc:
                self.log.error(exc)
                err = 'Invalid YAML in {0}. Aborting.'.format(self.filename)
                self.log.error(err)
                raise ConfigError(err)

        self.log.debug('Configuration file loaded.')

    def collect_classes(self):
        def traverse(data):
            # yield from :'(
            ret = []
            for key, value in data.items():
                if key == 'class':
                    ret.append(value)
                elif key == 'classes':
                    ret.extend(value)
                elif isinstance(value, dict):
                    ret.extend(traverse(value))

            return ret

        return set(traverse(self.raw))

    def load_classes(self):
        self.log.debug("Loading classes...")

        for cls in self.collect_classes():
            self.log.debug("Loading class '{0}()'".format(cls))
            self.classes[cls] = dynamic_load(cls)

        self.log.debug("Class loading done.")

    def validate_config(self):
        self.log.debug('Validating...')
        jsonschema.validate(self.raw, self.schema)

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


class BuildConfig(Config):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        'type': 'object',
        'additionalProperties': False,
        'required': ['version', 'envs', 'steps', 'pipelines'],
        'properties': {
            'version': {
                'description':
                    'Versioning setup for this project. This sets up what '
                    'commands to run to determine the version of the pipeline '
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
            'pipelines': {
                'description': 'Runnable collections of steps.',
                'type': 'object',
                'additionalProperties': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
            },
            'db': DB_SCHEMA,
            'pipeline': {
                'description': 'The key of the pipeline to execute.',
                'type': 'string',
            },
        },
    }

    def __init__(self, filename=None, raw=None):
        if raw is None and filename is None:
            filename = 'piper.yml'

        super(BuildConfig, self).__init__(filename, raw)


class AgentConfig(Config):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema",
        'type': 'object',
        'additionalProperties': False,
        'required': ['agent', 'db'],
        'properties': {
            'agent': {
                'description': 'Agent configuration',
                'type': 'object',
                'additionalProperties': False,
                'required': ['name', 'fqdn', 'active'],
                'properties': {
                    'name': {
                        'description':
                            'Descriptive name, used for display in interfaces',
                        'type': 'string',
                    },
                    'fqdn': {
                        'description':
                            'Fully qualified domain name, used for network '
                            'operations.',
                        'type': 'string',
                    },
                    'active': {
                        'description':
                            'Decides if the agent is to be used for building '
                            'or not. Inactive agents are connected and '
                            'visible, but will not be considered for any '
                            'tasks.',
                        'type': 'boolean',
                    },
                },
            },
            'db': DB_SCHEMA,
            'properties': {
                'description': 'Agent property configuration',
                'type': 'object',
                'additionalProperties': False,
                'required': ['classes'],
                'properties': {
                    'classes': {
                        'description': 'Classes to use for property loading',
                        'type': 'array',
                    },
                },
            },
        },
    }

    def __init__(self, filename=None):
        if not filename:
            filename = 'piperd.yml'

        super(AgentConfig, self).__init__(filename)
