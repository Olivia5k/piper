import contextlib
import json
import logbook

from piper.api import RESTful
from piper.build import Build
from piper.config import AgentConfig
from piper.config import BuildConfig
from piper.db.core import LazyDatabaseMixin
from piper.utils import oneshot


class Agent(LazyDatabaseMixin):
    """
    Listener endpoint that recieves requests and executes them

    """

    FIELDS_TO_DB = (
        # Main fields
        'id',
        'config',

        # Relationship fields
        'building',

        # Bulk data
        'properties',

        # Timestamps
        'created',
    )

    def __init__(self, config):
        self.config = config

        self.id = config.raw['agent']['id']
        self.building = None
        self._properties = None

        self.log = logbook.Logger(self.id)

    def register(self):
        agent = self.db.agent.get(self.id)
        if agent is None:
            self.log.info('Registering new agent.')
            self.db.agent.add(self.as_dict())

    def listen(self):
        """
        Listen for new requests

        """

        self.register()
        self.log.info('Opening changes() feed from database...')

        try:
            for change in self.db.build.feed():
                self.handle(change)

        except KeyboardInterrupt:  # pragma: nocover
            print()
            self.log.info('Kill signal recieved. Exiting.')

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

        id = change['new_val']['id']
        config = change['new_val']['config']
        self.log.info('Incoming request {0}'.format(id))

        # if self.id not in config.get('eligible_agents', []):
        #     self.log.info('Not able to build. Doing nothing.')
        #     return

        if config.get('started') is not None:
            self.log.info('Build already started. Doing nothing.')
            return

        return self.build(id, config)

    def build(self, id, config):
        """
        Run a build of a configuration.

        """

        with self.busy(id):
            # Set the config as being built by this agent.
            # config['agent'] = self

            config = BuildConfig(raw=config).load()
            self.log.info('Starting build...')

            build = Build(config)
            ret = build.run()

            self.log.debug('Build returned {0}'.format(ret))

    def update(self):
        """
        Update state of the agent in the database

        """

        data = self.as_dict()
        self.db.agent.update(data)

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

    @property
    def raw(self):  # pragma: nocover
        return self.id

    @contextlib.contextmanager
    def busy(self, id):
        """
        Context locker that sets and resets the `building` attribute.

        """

        self.building = id
        self.log.info('Locking for build {0}'.format(id))
        self.update()

        try:
            yield

        except Exception:
            self.log.exception('Build threw internal exception')

        finally:
            self.building = None
            self.log.info('Unlocking from build {0}'.format(id))
            self.update()


class AgentCLI(LazyDatabaseMixin):
    config_class = AgentConfig

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

    def run(self, ns):
        if self.config.agent_command in (None, 'start'):
            self.log.info('Starting agent')
            self.agent.listen()


class AgentAPI(RESTful):
    """
    API endpoint for CRUD operations on agents.

    """

    def __init__(self, config):
        super().__init__(config)
        self.routes = (
            ('GET', '/agents/{id}', self.get),
        )

    def get(self, request):
        """
        Get one agent.

        """

        id = request.match_info.get('id')
        agent = self.db.agent.get(id)

        if agent is None:
            return {}, 404

        return agent
