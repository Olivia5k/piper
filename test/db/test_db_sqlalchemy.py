from piper.db.db_sqlalchemy import SQLAlchemyDB
from piper.db.db_sqlalchemy import in_session

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


class TestSQLAlchemyDBGetOrCreate(SQLAlchemyDBBase):
    def setup_method(self, method):
        super(TestSQLAlchemyDBGetOrCreate, self).setup_method(method)
        self.session = mock.Mock()
        self.model = mock.Mock()
        self.kwargs = {'life is a grave': 'i dig it'}
        self.filter = self.session.query.return_value.filter_by

    def test_already_exists(self):
        ret = self.db.get_or_create(self.session, self.model, **self.kwargs)

        assert ret is self.filter.return_value.first.return_value
        assert self.session.add.call_count == 0

    def test_does_not_exist(self):
        self.filter.return_value.first.return_value = None

        self.db.get_or_create(self.session, self.model, **self.kwargs)

        self.model.assert_called_once_with(**self.kwargs)
        self.session.add.assert_called_once_with(self.model.return_value)


class TestInSessionInner(object):
    def setup_method(self, method):
        self.mock = mock.Mock()
        self.sql = mock.Mock()  # self instance for the call
        self.inner = in_session(self.mock)
        self.args = ['nutbush']
        self.kwargs = {'city': 'limits'}

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_return_value(self, session):
        ret = self.inner(*self.args, **self.kwargs)
        assert ret is self.mock.return_value

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_session_calls(self, session):
        self.inner(*self.args, **self.kwargs)
        session.assert_called_once_with()
        session.return_value.close.assert_called_once_with()

    @mock.patch('piper.db.db_sqlalchemy.Session')
    def test_args_and_kwargs(self, session):
        self.inner(self.sql, *self.args, **self.kwargs)
        self.mock.assert_called_once_with(
            self.sql,
            session.return_value,
            *self.args,
            **self.kwargs
        )
