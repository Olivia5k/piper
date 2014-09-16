from piper.db.core import DbCLI
from piper.db.core import DatabaseBase

import mock
import pytest


class DbCLIBase(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = DbCLI(self.config)
        self.ns = mock.Mock()


class TestDbCLIRun(DbCLIBase):
    def test_plain_run(self):
        self.cli.db.init = mock.Mock()
        ret = self.cli.run(self.ns)

        assert ret == 0
        self.cli.db.init.assert_called_once_with(self.ns)


class TestDatabaseBaseInit(object):
    def setup_method(self, method):
        self.db = DatabaseBase()
        self.ns = mock.Mock()
        self.config = mock.Mock()

    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            self.db.init(self.ns, self.config)
