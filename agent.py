import json
import logbook

from piper.db.core import LazyDatabaseMixin
from piper.utils import oneshot


class Agent(LazyDatabaseMixin):
    """
    Listener endpoint that recieves requests and executes them

    """

    _properties = None

    FIELDS_TO_DB = (
        # Main fields
        'id',
        'fqdn',
        'config',
        'local',
        'active',

        # Relationship fields
        'building',

        # Bulk data
        'properties',

        # Timestamps
        'created',
    )

    def __init__(self, config):
        self.config = config

        self.id = None
        self.building = None
        self.status = None

        self.log = logbook.Logger(self.__class__.__name__)

    def update(self):
        """
        Update state of the agent in the database

        """

        ...

    @property
    def properties(self):
        """
        Grab system properties for the agent. Will be cached once it's ran.

        :returns: Dictionary of system values

        """

        if self._properties is None:
            facter = oneshot('facter --json')
            data = json.loads(facter)

            self._properties = data

        return self._properties
