import pytest
import mock

from piper.prop import Prop
from piper.prop import FacterProp
from piper.prop import PropCLI


class PropTest(object):
    def setup_method(self, method):
        self.prop = Prop()


class PropCLITest(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = PropCLI(self.config)
        self.cli.db = mock.Mock()


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


class TestPropCLIRun(PropCLITest):
    def test_return_value(self):
        ret = self.cli.run()
        assert ret == 0

    def test_update(self):
        self.cli.config.prop_command = 'update'

        self.prop = mock.Mock()
        self.cli.config.classes = {
            'piper.prop.Test': self.prop,
        }

        ret = self.cli.run()
        assert ret == 0

        self.cli.db.property.update.assert_called_once_with([self.prop])

    def test_update_skips_non_prop_classes(self):
        self.cli.config.prop_command = 'update'

        self.prop = mock.Mock()
        self.cli.config.classes = {
            'piper.prop.Test': self.prop,
            'gotthard.bang.BangBang': None,
        }

        ret = self.cli.run()
        assert ret == 0

        self.cli.db.property.update.assert_called_once_with([self.prop])
