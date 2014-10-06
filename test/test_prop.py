import pytest
import mock

from piper.prop import Prop
from piper.prop import FacterProp


class PropTest(object):
    def setup_method(self, method):
        self.prop = Prop()


class TestPropProperties(PropTest):
    def test_properties_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.prop.properties


class TestPropNamespace(PropTest):
    def test_namespace(self):
        assert self.prop.namespace == 'piper.prop.Prop'


class TestPropFlatten(PropTest):
    def test_empty_dict(self):
        ret = self.prop.flatten({})

        assert ret == {}

    def test_one_level(self):
        d = {'reverend': 'horton heat'}
        ret = self.prop.flatten(d)

        assert ret == d

    def test_flattening(self):
        d = {
            'reverend': {
                'horton': 'heat',
            }
        }
        ret = self.prop.flatten(d)

        assert ret == {
            'reverend.horton': 'heat'
        }

    def test_flattening_multiple_levels(self):
        d = {
            'reverend': {
                'horton': {
                    'heat': True
                },
            }
        }
        ret = self.prop.flatten(d)

        assert ret == {
            'reverend.horton.heat': True
        }

    def test_flattening_list_items(self):
        d = {
            'reverend': {
                'horton': ['trouble', 'brucie'],
            }
        }
        ret = self.prop.flatten(d)

        assert ret == {
            'reverend.horton.0': 'trouble',
            'reverend.horton.1': 'brucie',
        }


class TestFacterPropProperties(object):
    @mock.patch('facter.Facter')
    def test_get_properties(self, Facter):
        self.prop = FacterProp()
        self.prop.flatten = mock.Mock()

        ret = self.prop.properties

        assert ret is self.prop._props
        assert ret is self.prop.flatten.return_value
        assert Facter.call_count == 1

        self.prop.flatten.assert_called_once_with(Facter.return_value.all)
