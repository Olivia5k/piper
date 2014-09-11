import pytest
import mock

from piper.prop import PropBase
from piper.prop import FacterProp


class TestPropBaseProperties(object):
    def test_properties_raises_notimplementederror(self):
        prop = PropBase(mock.Mock(), {})
        with pytest.raises(NotImplementedError):
            prop.properties


class TestFacterPropProperties(object):
    @mock.patch('facter.Facter')
    def test_get_properties(self, Facter):
        prop = FacterProp(mock.Mock(), {})
        ret = prop.properties

        assert Facter.call_count == 1
        assert ret is Facter.return_value.all
