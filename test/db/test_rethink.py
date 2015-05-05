import os
import time
import rethinkdb as rdb

from piper.db.rethink import RethinkDB
from piper.build import Build

from mock import Mock
from mock import call
from mock import patch

import pytest
from test import utils


@pytest.fixture
def piper():
    return utils.BASE_CONFIG


@pytest.fixture()
def rethink(request):
    """
    Set up a test database in Rethink and return a piper.db.rethink.RethinkDB
    instance.

    Tears down the database once done.

    """

    conn = rdb.connect(
        host=os.getenv('RETHINKDB_TEST_HOST', "localhost"),
        port=os.getenv('RETHINKDB_TEST_PORT', 28015),
    )

    db_name = 'piper_test_{0}'.format(str(time.time()).replace('.', '_'))
    rdb.db_create(db_name).run(conn)
    conn.use(db_name)

    rethink = RethinkDB()
    rethink.conn = conn  # Ugly faking to make the manager creation roll.
    rethink.create_tables(conn)

    def fin():
        rdb.db_drop(db_name).run(conn)
        pass

    request.addfinalizer(fin)

    return rethink


class RethinkDbTest:
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
        self.conn = Mock()


class TestRethinkDbSetup(RethinkDbTest):
    def test_setup_connection_call(self):
        self.rethinkdb.connect = Mock()
        self.rethinkdb.setup_managers = Mock()

        self.rethinkdb.setup(self.config)
        self.rethinkdb.connect.assert_called_once_with(self.config)
        self.rethinkdb.setup_managers.assert_called_once_with()


class TestRethinkDbConnect(RethinkDbTest):
    @patch('rethinkdb.connect')
    def test_conncetion(self, connect):
        self.rethinkdb.connect(self.config)
        connect.assert_called_once_with(
            host='serenity',
            port=108,
            db='dashboard.light',
            auth_key='',
        )


class TestRethinkDbInit(RethinkDbTest):
    @patch('rethinkdb.connect')
    def test_calls(self, connect):
        self.rethinkdb.create_database = Mock()
        self.rethinkdb.create_tables = Mock()

        self.rethinkdb.init(self.config)

        # Proper connection should be set up
        connect.assert_called_once_with(
            host='serenity',
            port=108,
            auth_key='',
        )

        conn = connect()
        # Database should be created
        self.rethinkdb.create_database.assert_called_once_with(
            self.config,
            conn
        )

        # Connection should be set to new db
        conn.use.assert_called_once_with('dashboard.light')

        # Tables should be created
        self.rethinkdb.create_tables.assert_called_once_with(conn)


class TestRethinkDbCreateDatabase(RethinkDbTest):
    @patch('rethinkdb.db_create')
    @patch('rethinkdb.db_list')
    def test_already_exists(self, db_list, db_create):
        db_list.return_value.run.return_value = ['dashboard.light']

        ret = self.rethinkdb.create_database(self.config, self.conn)

        assert ret is False
        assert db_create.call_count == 0

    @patch('rethinkdb.db_create')
    @patch('rethinkdb.db_list')
    def test_creation(self, db_list, db_create):
        db_list.return_value.run.return_value = []

        ret = self.rethinkdb.create_database(self.config, self.conn)

        assert ret is True
        db_create.assert_called_once_with('dashboard.light')


class TestRethinkDbCreateTables(RethinkDbTest):
    @patch('rethinkdb.table_list')
    def test_calls(self, table_list):
        managers = [Mock(table_name='one'), Mock(table_name='day')]
        tables = table_list.return_value.run.return_value

        self.rethinkdb.setup_managers = Mock(return_value=managers)
        self.rethinkdb.create_table = Mock()
        self.rethinkdb.create_tables(self.conn)

        calls = [
            call(tables, managers[0], self.conn),
            call(tables, managers[1], self.conn),
        ]

        self.rethinkdb.create_table.assert_has_calls(calls)


class TestRethinkDbCreateTable(RethinkDbTest):
    def setup_method(self, method):
        super(TestRethinkDbCreateTable, self).setup_method(method)
        self.manager = Mock(table_name='delorean')

    @patch('rethinkdb.table_create')
    def test_already_exists(self, table_create):
        ret = self.rethinkdb.create_table(
            ['delorean'],
            self.manager,
            self.conn
        )

        assert ret is False
        assert table_create.call_count == 0

    @patch('rethinkdb.table_create')
    def test_creation(self, table_create):
        ret = self.rethinkdb.create_table(
            [],
            self.manager,
            self.conn
        )

        assert ret is True
        table_create.assert_called_once_with(self.manager.table_name)


class TestRethinkDbIntegration:
    def test_build_add(self, rethink, piper):
        """
        Assert that one build was added

        """

        build = Build(piper)
        rethink.build.add(build)

        ret = rethink.build.table.run(rethink.conn)
        assert len(ret.items) == 1

    def test_build_update(self, rethink, piper):
        """
        Assert that build can be updated.

        """

        build = Build(piper)
        id = rethink.build.add(build)
        build.id = id

        ret = rethink.build.table.run(rethink.conn).next()
        assert ret['success'] is None

        build.success = True
        rethink.build.update(build)

        ret = rethink.build.table.run(rethink.conn)
        assert len(ret.items) == 1
        item = ret.next()
        assert item['success'] is True
