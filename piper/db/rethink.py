import logbook

from piper.db import core as db


class RethinkManager(object):
    def __init__(self, db):
        self.db = db

        self.log = logbook.Logger(self.__class__.__name__)


class AgentManager(RethinkManager, db.AgentManager):
    def get(self):
        raise NotImplementedError()

    def lock(self, build):
        self.set_lock(build, True)

    def unlock(self, build):
        self.set_lock(build, False)

    def set_lock(self, build, locked):
        raise NotImplementedError()


class BuildManager(RethinkManager, db.BuildManager):
    def add(self, build):
        raise NotImplementedError()

    def update(self, build, **extra):
        raise NotImplementedError()

    def get(self, build_id):
        raise NotImplementedError()

    def all(self):
        raise NotImplementedError()


class ConfigManager(RethinkManager, db.ConfigManager):
    def register(self, build, project=None):
        raise NotImplementedError()


class ProjectManager(RethinkManager, db.ProjectManager):
    def get(self, build):
        raise NotImplementedError()


class VCSManager(RethinkManager, db.VCSManager):
    def get(self, build):
        raise NotImplementedError()


class PropertyManager(RethinkManager, db.PropertyManager):
    def update(self, classes):
        raise NotImplementedError()


class PropertyNamespaceManager(RethinkManager, db.PropertyNamespaceManager):
    def get(self, name):
        raise NotImplementedError()


class RethinkDB(db.Database):
    def setup(self, config):
        raise NotImplementedError()

    def init(self, config):
        raise NotImplementedError()
