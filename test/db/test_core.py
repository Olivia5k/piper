from piper.db.core import LazyDatabaseMixin

import mock
import pytest

from piper.db.core import DbCLI
from piper.db.core import Database


@pytest.fixture
def lazy():
    lazy = LazyDatabaseMixin()
    lazy.FIELDS_TO_DB = (
        'id', 'test', 'hax'
    )
    return lazy


class DbCLITest:
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = DbCLI(self.config)
        self.cli.db = mock.Mock()


class TestDbCLIRun(DbCLITest):
    def test_plain_run(self):
        self.cli.db.init = mock.Mock()
        ret = self.cli.run()

        assert ret == 0
        self.cli.db.init.assert_called_once_with(self.config)


class TestDatabase:
    def setup_method(self, method):
        self.db = Database()

    def missing(self, ns, name, *args, **kwargs):
        target = self.db
        if ns is not None:
            target = getattr(self.db, ns)

        with pytest.raises(NotImplementedError):
            getattr(target, name)(*args, **kwargs)

    def test_everything_raises_not_implemented_error(self):
        self.mock = mock.Mock()

        self.missing(None, 'setup', self.mock)
        self.missing(None, 'init', self.mock)
        self.missing('build', 'add', self.mock)
        self.missing('build', 'update', self.mock)
        self.missing('build', 'get', self.mock)
        self.missing('build', 'all')
        self.missing('build', 'get_agents', self.mock)
        self.missing('config', 'register', self.mock)
        self.missing('project', 'get', self.mock)
        self.missing('vcs', 'get', self.mock)
        self.missing('agent', 'get')
        self.missing('agent', 'lock', self.mock)
        self.missing('agent', 'unlock', self.mock)
        self.missing('property', 'update')


class TestLazyDatabaseMixinDb:
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


class TestLazyDatabaseMixinAsDict(object):
    def test_without_id_key(self, lazy):
        ret = lazy.as_dict()
        assert 'id' not in ret

    def test_with_id_key(self, lazy):
        lazy.id = True  # Can't use a mock because it will have a .raw
        ret = lazy.as_dict()
        assert ret['id'] is lazy.id

    @mock.patch('piper.utils.now')
    def test_timestamp_is_added(self, now, lazy):
        ret = lazy.as_dict()
        assert ret['updated'] is now.return_value

    def test_raw_value(self, lazy):
        lazy.hax = mock.Mock()
        ret = lazy.as_dict()
        assert ret['hax'] is lazy.hax.raw
