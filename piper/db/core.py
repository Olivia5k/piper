import logbook


class LazyDatabaseMixin(object):
    """
    A mixin class that gives the subclass lazy access to the database layer

    The lazy attribute self.db is added, and the database class is gotten from
    self.config, and an instance is made and returned.

    """

    _db = None

    def _get_db(self):
        if self._db is None:
            assert hasattr(self, 'config') and self.config is not None, \
                'Database accessed before self.config was set.'

            self._db = self.config.get_database()
            self._db.setup(self.config)

        return self._db

    def _set_db(self, val):
        # This is actually mostly for tests so that we don't have to do the
        # mock-out-the-property dance for all the tests that hit the db.
        self._db = val

    db = property(_get_db, _set_db)


class AgentManager(object):
    def get(self):
        """
        Lazily get an agent.

        """

        raise NotImplementedError()

    def lock(self, build):
        """
        Lock the agent to a build.

        When an agent is locked, it will not accept other builds until it
        unlocks itself.

        """

        raise NotImplementedError()

    def unlock(self, build):
        """
        Unlock the agent from a build.

        """

        raise NotImplementedError()


class BuildManager(object):
    def add(self, build):
        """
        Register a build to the database.

        Should return a reference to the build that other methods can access
        via `self.ref`.

        """

        raise NotImplementedError()

    def update(self, build):
        """
        Update the state of a build.

        Uses `build.ref` as set by `add_build()`.

        """

        raise NotImplementedError()

    def get(self, build_id):
        """
        Get a build and all its related fields.

        Should return a Build object or None.

        """

        raise NotImplementedError()

    def all(self):
        """
        Get all builds!

        """

        raise NotImplementedError()


class ProjectManager(object):
    def get(self, build):
        """
        Lazily get the project.

        Create the project if it does not exist. If the VCS root for the
        project does not exist, create that too.

        """

        raise NotImplementedError()


class VCSManager(object):
    def get(self, build):
        """
        Lazily get the VCS.

        """

        raise NotImplementedError()


class PropertyManager(object):
    def update(self):
        """
        Update agent properties.

        """

        raise NotImplementedError()


class PropertyNamespaceManager(object):
    pass


class Database(object):
    """
    Abstract class representing a persistance layer

    """

    agent = AgentManager()
    build = BuildManager()
    project = ProjectManager()
    vcs = VCSManager()
    property = PropertyManager()
    propertynamespace = PropertyNamespaceManager()

    def __init__(self):
        self.log = logbook.Logger(self.__class__.__name__)

    def setup(self, config):
        """
        Set up the database.

        This should do whatever setup steps are needed for the database
        connection to be able to happen.

        """

        raise NotImplementedError()

    def init(self, config):
        """
        Create the tables needed for the application.

        """

        raise NotImplementedError()


class DbCLI(LazyDatabaseMixin):
    def __init__(self, config):
        self.config = config
        self.log = logbook.Logger(self.__class__.__name__)

    def compose(self, parser):  # pragma: nocover
        db = parser.add_parser('db', help='Perform database tasks')

        sub = db.add_subparsers(help='Database commands', dest="db_command")
        sub.add_parser('init', help='Do the initial setup of the database')

        return 'db', self.run

    def run(self):
        self.db.init(self.config)
        return 0
