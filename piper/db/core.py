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


# Let's name this DatabaseBase. 'tis a silly name.
class DatabaseBase(object):
    """
    Abstract class representing a persistance layer

    """

    def __init__(self):
        self.log = logbook.Logger(self.__class__.__name__)

    def init(self, ns):
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

    def run(self, ns):
        self.db.init(ns)
        return 0
