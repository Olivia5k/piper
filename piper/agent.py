import json
import logbook
import rethinkdb as rdb

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

    def listen(self):
        """
        Listen for new requests

        """

        for build in self.db.build.feed():
            self.log.debug(build)

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
            self.log.info('Grabbing fresh facter facts')
            facter = oneshot('facter --json')
            data = json.loads(facter)

            self._properties = data

        return self._properties


class AgentCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config
        self.agent = Agent(config)

        self.log = logbook.Logger(self.__class__.__name__)

    def compose(self, parser):  # pragma: nocover
        api = parser.add_parser('agent', help='Start or control agents')

        sub = api.add_subparsers(help='Agent commands', dest="agent_command")
        sub.add_parser('start', help='Start an agent')

        return 'agent', self.run

    def setup(self):  # pragma: nocover
        ...

    def run(self):
        if self.config.agent_command in (None, 'start'):
            self.log.info('Starting agent')
