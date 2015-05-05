from piper.utils import LimitedSizeDict
from piper.utils import dynamic_load
from piper.utils import oneshot

import pytest


class TestDynamicLoad:
    def test_proper_load(self):
        cls = dynamic_load('piper.utils.LimitedSizeDict')
        assert cls is LimitedSizeDict

    def test_nonexistant_target(self):
        with pytest.raises(ImportError):
            dynamic_load('gammaray.empire.Avalon')


class TestOneshot:
    def test_execution(self):
        ret = oneshot('echo lolz')
        assert ret == 'lolz'

    def test_failing_execution(self):
        with pytest.raises(Exception):
            oneshot('false')
