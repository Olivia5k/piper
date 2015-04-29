from piper.db.rethink import RethinkDB

from mock import patch
from mock import Mock


class TestRethinkDbSetup(object):
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

    @patch('rethinkdb.connect')
    def test_setup_connection_call(self, connect):
        self.rethinkdb.setup(self.config)
        assert self.rethinkdb._config is self.config

        connect.assert_called_once_with(
            host='serenity',
            port=108,
            db='dashboard.light',
            auth_key='',
        )
