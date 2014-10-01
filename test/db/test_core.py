from piper.db.core import LazyDatabaseMixin

import mock
import pytest

from piper.db.core import DbCLI
from piper.db.core import DatabaseBase


class DbCLIBase(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = DbCLI(self.config)
        self.cli.db = mock.Mock()


class TestDbCLIRun(DbCLIBase):
    def test_plain_run(self):
        self.cli.db.init = mock.Mock()
        ret = self.cli.run()

        assert ret == 0
        self.cli.db.init.assert_called_once_with(self.config)


class TestDatabaseBase(object):
    def setup_method(self, method):
        self.db = DatabaseBase()

    def missing(self, name, *args, **kwargs):
        with pytest.raises(NotImplementedError):
            getattr(self.db, name)(*args, **kwargs)

    def test_everything_raises_not_implemented_error(self):
        self.mock = mock.Mock()

        self.missing('setup', self.mock)
        self.missing('init', self.mock)
        self.missing('add_build', self.mock)
        self.missing('update_build', self.mock)
        self.missing('get_build', self.mock)
        self.missing('get_builds')
        self.missing('get_project', self.mock)
        self.missing('get_vcs', self.mock)
        self.missing('get_agent')
        self.missing('lock_agent', self.mock)
        self.missing('unlock_agent', self.mock)
        self.missing('update_props')


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
