import logbook
import rethinkdb as rdb

from piper.db import core as db


class RethinkManager:
    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.table = rdb.table(self.table_name)

        self.log = logbook.Logger(self.__class__.__name__)


class AgentManager(RethinkManager, db.AgentManager):
    table_name = 'agent'

    def get(self, id):
        return self.table.get(id).run(self.conn)

    def add(self, data):
        return self.table.insert(data).run(self.conn)

    def update(self, data):
        self.table.replace(data).run(self.conn)


class BuildManager(RethinkManager, db.BuildManager):
    table_name = 'build'

    def add(self, build):
        # TODO: Error handling
        data = build.as_dict()
        ret = self.table.insert(data).run(self.conn)

        return ret['generated_keys'][0]

    def update(self, build):
        data = build.as_dict()
        return self.table.update(data).run(self.conn)

    def get(self, id):
        return self.table.get(id).run(self.conn)

    def all(self):
        raise NotImplementedError()

    def feed(self):
        return self.table.changes().run(self.conn)


class RethinkDB(db.Database):
    managers = (
        AgentManager,
        BuildManager,
    )

    def setup(self, config):
        """
        Used for setting up a session when starting piper

        """

        self.conn = self.connect(config)
        self.setup_managers()

    def init(self, config):
        """
        Used for initial creation of database when none exists.
        Used by `piperd db init`

        """

        conn = rdb.connect(
            host=config.raw['db']['host'],
            port=config.raw['db']['port'],
            auth_key=config.raw['db'].get('auth_key', ''),
        )

        self.create_database(config, conn)
        conn.use(config.raw['db']['db'])
        self.create_tables(conn)

    def create_database(self, config, conn):
        """
        Idempotently try to create the database

        """

        db = config.raw['db']['db']
        dbs = rdb.db_list().run(conn)

        if db not in dbs:
            self.log.info(
                'Database {0} does not exist. Creating it...'.format(db)
            )
            rdb.db_create(db).run(conn)
            return True

        self.log.info('Database already exists.')
        return False

    def create_tables(self, conn):
        tables = rdb.table_list().run(conn)
        for man in self.setup_managers():
            self.create_table(tables, man, conn)

    def create_table(self, tables, man, conn):
        """
        Idempotently create a table

        """

        name = man.table_name

        if name in tables:
            self.log.info(
                "Table '{0}' already exists.".format(name)
            )
            return False

        self.log.info("Creating table '{0}'...".format(name))
        rdb.table_create(name).run(conn)
        return True

    def connect(self, config):
        """
        Start a connection to RethinkDB.

        """

        self.log.debug(
            'Connecting to {host}:{port}/{db}'.format(**config.raw['db'])
        )

        # TODO: Error handling if connection refused.
        return rdb.connect(
            host=config.raw['db']['host'],
            port=config.raw['db']['port'],
            db=config.raw['db']['db'],
            auth_key=config.raw['db'].get('auth_key', ''),
        )

    def setup_managers(self):
        """
        Create instances of all manager classes, setting them as attributes
        with the same name as their table names.

        """

        ret = []
        for manager in self.managers:
            man = manager(self)
            setattr(self, man.table_name, man)
            ret.append(man)

        return ret
