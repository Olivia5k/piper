from piper.utils import DotDict
from piper.utils import dynamic_load

import pytest


class TestDotDict(object):
    def test_get_nonexistant_raises_keyerror(self):
        with pytest.raises(KeyError):
            dd = DotDict({})
            dd.does_not_exist

    def test_get_item(self):
        dd = DotDict({'danger': 'zone'})
        assert dd.danger == 'zone'

    def test_get_item_dict_access(self):
        dd = DotDict({'danger': 'zone'})
        assert dd['danger'] == 'zone'

    def test_dict_items_become_dotdicts(self):
        dd = DotDict({'highway': {'danger': 'zone'}})
        assert isinstance(dd.highway, DotDict) is True

    def test_nested_access(self):
        dd = DotDict({'highway': {'danger': {'zone': True}}})
        assert dd.highway.danger.zone is True


class TestDynamicLoad(object):
    def test_proper_load(self):
        cls = dynamic_load('piper.utils.DotDict')
        assert cls is DotDict

    def test_nonexistant_target(self):
        with pytest.raises(ImportError):
            dynamic_load('gammaray.empire.Avalon')
