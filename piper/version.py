import logbook
import jsonschema

from piper.utils import DotDict
from piper.utils import oneshot


class Version(object):
    """
    Base for versioning classes

    """

    def __init__(self, ns, config):
        self.ns = ns
        self.config = DotDict(config)
        self.log = logbook.Logger(self.__class__.__name__)

    def __str__(self):  # pragma: nocover
        return self.get_version()

    def __repr__(self):  # pragma: nocover
        return self.__str__()

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = {
                '$schema': 'http://json-schema.org/draft-04/schema',
                'type': 'object',
                'additionalProperties': False,
                'required': ['class'],
                'properties': {
                    'class': {
                        'description':
                            'Python class to load to determine versions',
                        'type': 'string',
                    },
                },
            }

        return self._schema

    def validate(self):
        jsonschema.validate(self.config.data, self.schema)

    def get_version(self):
        raise NotImplementedError()


class StaticVersion(Version):
    """
    Static versioning, set inside the piper.yml configuration file

    """

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = super(StaticVersion, self).schema
            self._schema['required'].append('version')
            self._schema['properties']['version'] = {
                'description': 'Static version to use',
                'type': 'string',
            }

        return self._schema

    def get_version(self):
        return self.config.version


class GitVersion(Version):
    """
    Versioning based on the output of `git describe`

    """

    def __init__(self, ns, config):
        super(GitVersion, self).__init__(ns, config)
        if 'arguments' not in config.data:
            self.config.arguments = None

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = super(GitVersion, self).schema
            self._schema['properties']['arguments'] = {
                'description':
                    'Space separated arguments passed directly to the '
                    '`git describe` call. Default is none. You probably want '
                    'to add `--tags` if you are not using annotated tags.',
                'type': 'string',
            }

        return self._schema

    def get_version(self):
        cmd = 'git describe'

        if self.config.arguments:
            cmd += ' ' + self.config.arguments

        return oneshot(cmd)
