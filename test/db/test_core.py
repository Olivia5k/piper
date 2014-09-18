from piper.db.core import LazyDatabaseMixin

import mock
import pytest

from piper.db.core import DbCLI
from piper.db.core import DatabaseBase


class DbCLIBase(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = DbCLI(self.config)
        self.ns = mock.Mock()


class DatabaseBaseTestBase(object):  # <3
    def setup_method(self, method):
        self.db = DatabaseBase()
        self.ns = mock.Mock()
        self.config = mock.Mock()


class TestDbCLIRun(DbCLIBase):
    def test_plain_run(self):
        self.cli.db.init = mock.Mock()
        ret = self.cli.run(self.ns)

        assert ret == 0
        self.cli.db.init.assert_called_once_with(self.ns)


class TestDatabaseBaseInit(DatabaseBaseTestBase):
    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            self.db.init(self.ns)


class TestDatabaseBaseNewBuild(DatabaseBaseTestBase):
    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            self.db.new_build(mock.Mock())


class TestDatabaseBaseUpdateBuild(DatabaseBaseTestBase):
    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            self.db.update_build(mock.Mock())


class TestLazyDatabaseMixinDb(object):
    def setup_method(self, method):
        self.ldm = LazyDatabaseMixin()

    def test_config_raises_assert_error_if_not_set(self):
        with pytest.raises(AssertionError):
            self.ldm.db

    def test_config_raises_assert_error_if_none(self):
        self.ldm.config = None
        with pytest.raises(AssertionError):
            self.ldm.db

    def test_db_gets_grabbed(self):
        self.ldm.config = mock.Mock()

        self.ldm.db

        self.ldm.config.get_database.assert_called_once_with()

    def test_db_gets_configured(self):
        self.ldm.config = mock.Mock()

        self.ldm.db

        db = self.ldm.config.get_database.return_value
        db.setup.assert_called_once_with(self.ldm.config)

    def test_db_return_value(self):
        self.ldm.config = mock.Mock()

        ret = self.ldm.db

        db = self.ldm.config.get_database.return_value
        assert ret is db
