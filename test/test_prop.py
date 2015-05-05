import pytest
import mock

from piper.prop import Prop
from piper.prop import PropSource
from piper.prop import FacterPropSource
from piper.prop import PropCLI
from piper.prop import PropValidationError


class PropTest:
    def setup_method(self, method):
        self.key = 'nocturnal.rites'
        self.value = 'awakening'

        self.prop = Prop(self.key, self.value)
        self.prop.db = mock.Mock()


class PropSourceTest:
    def setup_method(self, method):
        self.build = mock.Mock()
        self.prop = PropSource()


class PropCLITest:
    def setup_method(self, method):
        self.config = mock.Mock()
        self.cli = PropCLI(self.config)
        self.cli.db = mock.Mock()


class TestPropValue(PropTest):
    def test_grab(self):
        self.prop._value = None
        ret = self.prop.value

        get = self.prop.db.property.get

        assert ret is get.return_value
        get.assert_called_once_with(self.prop.source.namespace, self.prop.key)

    def test_cached(self):
        ret = self.prop.value
        assert ret is self.value


class TestPropEquals(PropTest):
    def test_truth(self):
        self.prop.equals('awakening')

    def test_lies(self):
        with pytest.raises(PropValidationError):
            self.prop.equals('new.world.messiah')


class TestPropValidate(PropTest):
    def setup_method(self, method):
        super(TestPropValidate, self).setup_method(method)
        self.schema = {
            'reason': "John Wayne is not dead, he's frozen",
            'class': 'denisleary.cancer',
            'key': 'virtual',
            'equals': 'physical',
        }

    def test_passing_validation(self):
        self.prop.equals = mock.Mock()
        self.prop.validate(self.schema)

        self.prop.equals.assert_called_once_with('physical')

    def test_not_implemented_method(self):
        with pytest.raises(NotImplementedError):
            self.prop.validate({'hehe': None})


class TestPropToKwargs(PropTest):
    def test_no_extra(self):
        ret = self.prop.to_kwargs()
        assert ret == {
            'value': self.value,
            'key': self.key,
        }

    def test_with_extra(self):
        ret = self.prop.to_kwargs(hehe='hehe')
        assert ret == {
            'value': self.value,
            'key': self.key,
            'hehe': 'hehe',
        }


class TestPropSourceGenerate(PropSourceTest):
    def test_properties_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.prop.generate()


class TestPropSourceNamespace(PropSourceTest):
    def test_namespace(self):
        assert self.prop.namespace == 'piper.prop.Prop'


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


class TestFacterPropGenerate:
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
