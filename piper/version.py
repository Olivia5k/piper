from piper.abc import DynamicItem
from piper.utils import oneshot


class Version(DynamicItem):
    """
    Base for versioning classes

    """

    def __str__(self):  # pragma: nocover
        return self.get_version()

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
        return self.config['version']


class GitVersion(Version):
    """
    Versioning based on the output of `git describe`

    """

    @property
    def schema(self):
        if not hasattr(self, '_schema'):
            self._schema = super(GitVersion, self).schema
            self._schema['properties']['arguments'] = {
                'description':
                    'Space separated arguments passed directly to the '
                    '`git describe` call.',
                'default': "--tags",
                'type': 'string',
            }

        return self._schema

    def get_version(self):
        cmd = 'git describe'

        if self.config['arguments']:
            cmd += ' ' + self.config['arguments']
        return oneshot(cmd)
