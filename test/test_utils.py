from piper.utils import DotDict
from piper.utils import dynamic_load
from piper.utils import oneshot

import pytest


class TestDotDict(object):
    def test_get_nonexistant_gives_none(self):
        dd = DotDict({})
        dd.does_not_exist is None

    def test_get_item(self):
        dd = DotDict({'danger': 'zone'})
        assert dd.danger == 'zone'

    def test_get_item_dict_access(self):
        dd = DotDict({'danger': 'zone'})
        assert dd['danger'] == 'zone'

    def test_dict_items_become_dotdicts(self):
        dd = DotDict({'highway': {'danger': 'zone'}})
        assert isinstance(dd.highway, DotDict) is True

    def test_dict_items_become_dotdicts_when_using_dict_access(self):
        dd = DotDict({'highway': {'danger': 'zone'}})
        assert isinstance(dd['highway'], DotDict) is True

    def test_nested_access(self):
        dd = DotDict({'highway': {'danger': {'zone': True}}})
        assert dd.highway.danger.zone is True

    def test_make_dotdict_out_of_dotdict_does_not_nest(self):
        data = {'another': {'angel': 'down'}}
        dd1 = DotDict(data)
        dd2 = DotDict(dd1)
        assert dd1.data == dd2.data

    def test_equality_to_dict(self):
        data = {'fortune': 'fame'}
        dd = DotDict(data)

        assert dd.__eq__(data) is True
        assert dd.__eq__({}) is False

    def test_equality_to_dotdict(self):
        data = {'fame': 'fortune'}
        dd = DotDict(data)

        assert dd.__eq__(DotDict(data)) is True
        assert dd.__eq__(DotDict({})) is False

    def test_equality_to_others(self):
        dd = DotDict({})
        assert dd.__eq__(pytest.raises) is False

    def test_iter_is_dict_iter(self):
        data = {'reign': 'madness'}
        dd = DotDict(data)

        assert [x for x in dd] == [x for x in dd.data]


class TestDynamicLoad(object):
    def test_proper_load(self):
        cls = dynamic_load('piper.utils.DotDict')
        assert cls is DotDict

    def test_nonexistant_target(self):
        with pytest.raises(ImportError):
            dynamic_load('gammaray.empire.Avalon')


class TestOneshot(object):
    def test_execution(self):
        ret = oneshot('echo lolz')
        assert ret == 'lolz'

    def test_failing_execution(self):
        with pytest.raises(Exception):
            oneshot('false')
