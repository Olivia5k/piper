import facter

from piper.abc import DynamicItem


class PropBase(DynamicItem):
    @property
    def properties(self):
        """
        Collect system properties and return a dictionary of them

        """

        raise NotImplementedError()


class FacterProp(PropBase):
    """
    Collect properties from facter via facterpy

    It should be noted that the current version does not have any typecasting,
    so everything is always strings.
    See https://github.com/knorby/facterpy/issues/5

    """

    @property
    def properties(self):
        # Facter has its own caching, so we can safely just always run this.
        return facter.Facter().all
