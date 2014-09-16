from piper.db.core import LazyDatabaseMixin

import mock
import pytest


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
        db.setup.assert_called_once_with()

    def test_db_return_value(self):
        self.ldm.config = mock.Mock()

        ret = self.ldm.db

        db = self.ldm.config.get_database.return_value
        assert ret is db
