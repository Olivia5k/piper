import facter
import logbook
from collections import MutableMapping

from piper.db.core import LazyDatabaseMixin


class PropValidationError(Exception):
    def __init__(self, msg="", key=None, value=None, other=None,
                 namespace=None):
        self.msg = msg
        self.key = key
        self.value = value
        self.other = other
        self.namespace = namespace

        super(PropValidationError, self).__init__(self.msg)


class PropSource(object):
    def __init__(self):
        self._props = None

        self.log = logbook.Logger(self.__class__.__name__)

    def generate(self):
        """
        Collect system properties and return a dictionary of them

        """

        raise NotImplementedError()

    @property
    def namespace(self):
        return '.'.join((
            self.__module__, self.__class__.__name__.replace('Source', '')
        ))

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


class Prop(LazyDatabaseMixin):
    source = PropSource()

    def __init__(self, key, value=None):
        self.key = key
        self._value = value

    def __str__(self):  # pragma: nocover
        return '{0}: {1}'.format(self.key, self.value)

    @property
    def value(self):
        if self._value is None:
            self._value = self.db.property.get(
                self.source.namespace,
                self.key
            )

        return self._value

    def to_kwargs(self, **extra):
        kwargs = {
            'value': self.value,
            'key': self.key,
        }
        kwargs.update(extra)
        return kwargs

    def validate(self, schema):
        for field in schema:
            if field not in ('reason', 'class', 'key'):
                break

        method = getattr(self, field, None)
        if method is None:
            raise NotImplementedError(
                '`{0}` is not a known validation method'.format(field)
            )

        # Call the comparison method with the value provided.
        method(schema[field])

    def equals(self, other):
        if not self.value == other:
            raise PropValidationError(
                '`{0}` does not equal `{1}`'.format(self.value, other),
                key=self.key,
                value=self.value,
                other=other,
                namespace=self.source.namespace
            )


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
                self._props.append(FacterProp(key, value))
            self._props = sorted(self._props, key=lambda x: x.key)

        return self._props


class FacterProp(Prop):
    source = FacterPropSource()


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
