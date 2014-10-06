import facter
from collections import MutableMapping

from piper.db.core import LazyDatabaseMixin


class Prop(object):
    def __init__(self, source, key, value):
        self.source = source
        self.key = key
        self.value = value

    def equals(self, other):
        return self.value == other


class PropSource(object):
    def __init__(self):
        self._props = None

    def generate(self):
        """
        Collect system properties and return a dictionary of them

        """

        raise NotImplementedError()

    @property
    def namespace(self):
        return '.'.join((self.__module__, self.__class__.__name__))

    # http://stackoverflow.com/questions/6027558
    def flatten(self, d, parent_key='', sep='.'):
        items = []

        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k

            if isinstance(v, MutableMapping):
                items.extend(self.flatten(v, new_key).items())
            elif isinstance(v, list):
                # Make lists have keys like 'foo.bar.x'
                for x, item in enumerate(v):
                    key = '{2}{0}{1}'.format(sep, x, new_key)
                    items.append((key, item))
            else:
                items.append((new_key, v))

        return dict(items)


class FacterProp(Prop):
    pass


class FacterPropSource(PropSource):
    """
    Collect properties from facter via facterpy

    It should be noted that the current version does not have any typecasting,
    so everything is always strings.
    See https://github.com/knorby/facterpy/issues/5

    """

    def generate(self):
        if self._props is None:
            self._props = []
            facts = facter.Facter().all

            for key, value in self.flatten(facts).items():
                self._props.append(FacterProp(self, key, value))

        return self._props


class PropCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('prop', help='Control agent properties')

        sub = api.add_subparsers(help='Prop commands', dest="prop_command")
        sub.add_parser('update', help='Update properties')

        return 'prop', self.run

    def run(self):
        if self.config.prop_command == 'update':
            classes = []
            for key, cls in self.config.classes.items():
                if key.startswith('piper.prop.'):
                    classes.append(cls)

            self.db.property.update(classes)

        return 0
