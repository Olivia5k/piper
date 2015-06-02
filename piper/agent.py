import json
import logbook

from piper.build import Build
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

        for change in self.db.build.feed():
            self.handle(change)

    def handle(self, change):
        """
        Handle a changeset from Rethink.

        Will check for whether the changeset is eligible to be built. It is not
        if:
        * The build has been deleted.
        * This agent ID is not present in the `eligible_agents` list.
        * The build is already started by another agent.

        By default the changes are squashed and only the latest state of the
        changeset is sent to this function. See the
        `RethinkDB documentation <http://rethinkdb.com/api/python/changes/>`_.

        """

        self.log.debug(change)

        if change['new_val'] is None:
            # Request has been deleted. This is not really supposed to happen,
            # but might happen because of administrative reasons. Just don't
            # handle the request.
            self.log.warn(
                'Incoming request {id} was deleted'.format(**change['old_val'])
            )
            return False

        config = change['new_val']
        self.log.info('Incoming request {0}'.format(config['id']))

        if self.id not in config.get('eligible_agents', []):
            self.log.info('Not able to build. Doing nothing.')
            return

        if config.get('started') is not None:
            self.log.info('Build already started. Doing nothing.')
            return

        self.log.info('Starting build...')
        return Build(config).run()

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
