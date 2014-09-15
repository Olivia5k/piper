from piper.db import DbCLI

import mock


class DbCLIBase(object):
    def setup_method(self, method):
        self.cli = DbCLI(mock.Mock())
        self.ns = mock.Mock()
        self.config = mock.Mock()


class TestDbCLIRun(DbCLIBase):
    def test_plain_run(self):
        self.cli.cls.init = mock.Mock()
        ret = self.cli.run(self.ns, self.config)

        assert ret == 0
        self.cli.cls.init.assert_called_once_with(self.ns, self.config)
