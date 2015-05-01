import logbook
import rethinkdb as rdb

from piper.db import core as db


class RethinkManager(object):
    def __init__(self, db):
        self.db = db
        self.table = db.conn.table(self.table_name)

        self.log = logbook.Logger(self.__class__.__name__)


class AgentManager(RethinkManager, db.AgentManager):
    table_name = 'agent'

    def get(self):
        raise NotImplementedError()

    def lock(self, build):
        self.set_lock(build, True)

    def unlock(self, build):
        self.set_lock(build, False)

    def set_lock(self, build, locked):
        raise NotImplementedError()


class BuildManager(RethinkManager, db.BuildManager):
    table_name = 'build'

    def add(self, build):
        pass

    def update(self, build, **extra):
        raise NotImplementedError()

    def get(self, build_id):
        raise NotImplementedError()

    def all(self):
        raise NotImplementedError()


class ConfigManager(RethinkManager, db.ConfigManager):
    table_name = 'config'

    def register(self, build, project=None):
        pass


class ProjectManager(RethinkManager, db.ProjectManager):
    table_name = 'project'

    def get(self, build):
        raise NotImplementedError()


class VCSManager(RethinkManager, db.VCSManager):
    table_name = 'vcs'

    def get(self, build):
        raise NotImplementedError()


class PropertyManager(RethinkManager, db.PropertyManager):
    table_name = 'property'

    def update(self, classes):
        raise NotImplementedError()


class PropertyNamespaceManager(RethinkManager, db.PropertyNamespaceManager):
    table_name = 'property_namespace'

    def get(self, name):
        raise NotImplementedError()


class RethinkDB(db.Database):
    managers = (
        AgentManager,
        BuildManager,
        ConfigManager,
        ProjectManager,
        VCSManager,
        PropertyManager,
        PropertyNamespaceManager,
    )

    def setup(self, config):
        """
        Used for setting up a session when starting piper

        """

        self._config = config
        # TODO: Error handling if connection refused.
        self.conn = rdb.connect(
            host=config.raw['db']['host'],
            port=config.raw['db']['port'],
            db=config.raw['db']['db'],
            auth_key=config.raw['db'].get('auth_key', ''),
        )

        self.setup_managers()

    def init(self, config):
        """
        Used for initial creation of database when none exists.
        Used by `piperd db init`

        """

        raise NotImplementedError()

    def setup_managers(self):
        """
        Create instances of all manager classes, setting them as attributes
        with the same name as their table names.

        """

        for manager in self.managers:
            man = manager(self)
            setattr(self, man.table_name, man)
