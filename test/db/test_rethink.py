from piper.db.rethink import RethinkDB

from mock import patch
from mock import Mock


class RethinkDbTest(object):
    def setup_method(self, method):
        self.rethinkdb = RethinkDB()
        self.config = Mock()
        self.config.raw = {
            'db': {
                'host': 'serenity',
                'port': 108,
                'db': 'dashboard.light',
            }
        }


class TestRethinkDbSetup(RethinkDbTest):
    def test_setup_connection_call(self):
        self.rethinkdb.connect = Mock()

        self.rethinkdb.setup(self.config)
        assert self.rethinkdb._config is self.config
        self.rethinkdb.connect.assert_called_once_with()


class TestRethinkDbConnect(RethinkDbTest):
    def setup_method(self, method):
        super(TestRethinkDbConnect, self).setup_method(method)
        self.rethinkdb._config = self.config

    @patch('rethinkdb.connect')
    def test_conncetion(self, connect):
        self.rethinkdb.connect()
        connect.assert_called_once_with(
            host='serenity',
            port=108,
            db='dashboard.light',
            auth_key='',
        )
