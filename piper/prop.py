import facter
from collections import MutableMapping

from piper.abc import DynamicItem


class PropBase(DynamicItem):
    def __init__(self):
        super(PropBase, self).__init__(None)
        self._props = None

    @property
    def properties(self):
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
            else:
                items.append((new_key, v))

        return dict(items)


class FacterProp(PropBase):
    """
    Collect properties from facter via facterpy

    It should be noted that the current version does not have any typecasting,
    so everything is always strings.
    See https://github.com/knorby/facterpy/issues/5

    """

    @property
    def properties(self):
        if self._props is None:
            facts = facter.Facter().all
            self._props = self.flatten(facts)

        return self._props
