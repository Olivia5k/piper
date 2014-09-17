from piper.db.db_sqlalchemy import SQLAlchemyDB

import mock
import pytest


class SQLAlchemyDBBase(object):
    def setup_method(self, method):
        self.db = SQLAlchemyDB()
        self.ns = mock.Mock()
        self.config = mock.Mock()


class TestSQLAlchemyDBSetup(SQLAlchemyDBBase):
    @mock.patch('piper.db.db_sqlalchemy.create_engine')
    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_setup(self, se, ce):
        config = mock.Mock()
        self.db.setup(config)

        assert self.db.config is config
        ce.assert_called_once_with(config.db.host)
        se.configure.assert_called_once_with(bind=ce.return_value)


class TestSQLAlchemyDBInit(SQLAlchemyDBBase):
    def test_no_db(self):
        self.config.db.host = None

        with pytest.raises(AssertionError):
            self.db.init(self.ns, self.config)

    def test_calls(self):
        self.db.handle_sqlite = mock.Mock()
        self.db.create_tables = mock.Mock()

        self.db.init(self.ns, self.config)

        self.db.handle_sqlite.assert_called_once_with(self.config.db.host)
        self.db.create_tables.assert_called_once_with(
            self.config.db.host,
            echo=self.ns.verbose,
        )


class TestSQLAlchemyDBHandleSqlite(SQLAlchemyDBBase):
    @mock.patch('piper.utils.mkdir')
    @mock.patch('os.path.dirname')
    @mock.patch('os.path.exists')
    def test_sqlite_handling_creates_dir(self, exists, dirname, mkdir):
        self.config.db.host = 'sqlite:///amaranthine.db'
        exists.return_value = False

        self.db.handle_sqlite(self.ns.host)
        mkdir.assert_called_once_with(dirname.return_value)


class TestSQLAlchemyDBCreateTables(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBCreateTables, self).setup_method(method)
        self.db.tables = (mock.Mock(), mock.Mock())

        for x, table in enumerate(self.db.tables):
            table.__tablename__ = x

    @mock.patch('piper.db.db_sqlalchemy.Session')
    @mock.patch('piper.db.db_sqlalchemy.create_engine')
    def test_creation(self, ce, se):
        eng = ce.return_value
        host = self.config.host

        self.db.create_tables(host)

        ce.assert_called_once_with(host, echo=False)
        se.configure.assert_called_once_with(bind=eng)

        for table in self.db.tables:
            assert table.metadata.bind is eng
            table.metadata.create_all.assert_called_once_with()
