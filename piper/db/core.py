import logbook


# Let's name this DatabaseBase. 'tis a silly name.
class DatabaseBase(object):
    """
    Abstract class representing a persistance layer

    """

    def __init__(self):
        self.log = logbook.Logger(self.__class__.__name__)

    def init(self, ns, config):
        raise NotImplementedError()


class DbCLI(object):
    def __init__(self, cls):
        self.cls = cls
        self.log = logbook.Logger(self.__class__.__name__)

    def compose(self, parser):  # pragma: nocover
        db = parser.add_parser('db', help='Perform database tasks')

        sub = db.add_subparsers(help='Database commands', dest="db_command")
        sub.add_parser('init', help='Do the initial setup of the database')

        return 'db', self.run

    def run(self, ns, config):
        self.cls.init(ns, config)
        return 0
