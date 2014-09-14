from piper.db import DbCLI

import mock
import pytest


class DbCLIBase(object):
    def setup_method(self, method):
        self.cli = DbCLI()
        self.ns = mock.Mock()
        self.config = mock.Mock()


class TestDbCLIRun(DbCLIBase):
    def test_plain_run(self):
        self.cli.init = mock.Mock()
        ret = self.cli.run(self.ns, self.config)

        assert ret == 0
        self.cli.init.assert_called_once_with(self.ns, self.config)


class TestDbCLIInit(DbCLIBase):
    def test_no_db(self):
        self.config.db.host = None

        with pytest.raises(AssertionError):
            self.cli.init(self.ns, self.config)

    def test_calls(self):
        self.cli.handle_sqlite = mock.Mock()
        self.cli.create_tables = mock.Mock()

        self.cli.init(self.ns, self.config)

        self.cli.handle_sqlite.assert_called_once_with(self.config.db.host)
        self.cli.create_tables.assert_called_once_with(
            self.config.db.host,
            echo=self.ns.verbose,
        )


class TestDbCLIHandleSqlite(DbCLIBase):
    @mock.patch('piper.utils.mkdir')
    @mock.patch('os.path.dirname')
    @mock.patch('os.path.exists')
    def test_sqlite_handling_creates_dir(self, exists, dirname, mkdir):
        self.config.db.host = 'sqlite:///amaranthine.db'
        exists.return_value = False

        self.cli.handle_sqlite(self.ns.host)
        mkdir.assert_called_once_with(dirname.return_value)


class TestDbCLICreateTables(DbCLIBase):
    def setup_method(self, method):
        super(TestDbCLICreateTables, self).setup_method(method)
        self.cli.tables = (mock.Mock(), mock.Mock())

        for x, table in enumerate(self.cli.tables):
            table.__tablename__ = x

    @mock.patch('piper.db.Session')
    @mock.patch('piper.db.create_engine')
    def test_creation(self, ce, se):
        eng = ce.return_value
        host = self.config.host

        self.cli.create_tables(host)

        ce.assert_called_once_with(host, echo=False)
        se.configure.assert_called_once_with(bind=eng)

        for table in self.cli.tables:
            assert table.metadata.bind is eng
            table.metadata.create_all.assert_called_once_with()
