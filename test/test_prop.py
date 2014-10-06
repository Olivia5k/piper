import pytest
import mock

from piper.prop import Prop
from piper.prop import PropSource
from piper.prop import FacterPropSource
from piper.prop import PropCLI


class PropTest(object):
    def setup_method(self, method):
        self.source = mock.Mock()
        self.key = 'nocturnal.rites'
        self.value = 'awakening'
        self.prop = Prop(self.source, self.key, self.value)


class PropSourceTest(object):
    def setup_method(self, method):
        self.build = mock.Mock()
        self.prop = PropSource()


class PropCLITest(object):
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = PropCLI(self.config)
        self.cli.db = mock.Mock()


class TestPropEquals(PropTest):
    def test_truth(self):
        ret = self.prop.equals('awakening')
        assert ret is True

    def test_lies(self):
        ret = self.prop.equals('new.world.messiah')
        assert ret is False


class TestPropSourceGenerate(PropSourceTest):
    def test_properties_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.prop.generate()


class TestPropSourceNamespace(PropSourceTest):
    def test_namespace(self):
        assert self.prop.namespace == 'piper.prop.PropSource'


class TestPropSourceFlatten(PropSourceTest):
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


class TestFacterPropGenerate(object):
    @mock.patch('piper.prop.FacterProp')
    @mock.patch('facter.Facter')
    def test_generate(self, Facter, FacterProp):
        self.prop = FacterPropSource()
        self.prop.flatten = mock.Mock()
        self.prop.flatten.return_value = {
            'meredith.brooks': 'bitch',
        }

        ret = self.prop.generate()

        assert Facter.call_count == 1
        assert ret is self.prop._props
        assert ret == [FacterProp.return_value]

        FacterProp.assert_called_once_with(
            self.prop,
            'meredith.brooks',
            'bitch',
        )

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
