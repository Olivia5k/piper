import pytest

from piper.core import Environment


class TestEnvironment(object):
    def setup_method(self, method):
        self.env = Environment({})

    def test_execute_raises_notimplemented(self):
        with pytest.raises(NotImplementedError):
            self.env.execute()
