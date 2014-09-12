from piper.step import StepBase
from piper.step import CommandLineStep

import mock
import pytest


class StepTestBase(object):
    def setup_method(self, method):
        self.step = StepBase(
            mock.Mock(),
            {'class': 'piper.step.Class'},
            'key'
        )


class TestStepBaseValidate(StepTestBase):
    @mock.patch('jsonschema.validate')
    def test_validate(self, jv):
        self.step.validate()
        jv.assert_called_once_with(self.step.config.data, self.step.schema)

    def test_validation(self):
        self.step.validate()

    def test_validation_with_single_depends(self):
        self.step.config.data['depends'] = 'step'
        self.step.validate()

    def test_validation_with_multiple_depends(self):
        self.step.config.data['depends'] = ['step', 'singleton']
        self.step.validate()


class TestStepBaseSetIndex(StepTestBase):
    def test_set_index(self):
        index, total = mock.Mock(), mock.Mock()
        self.step.set_index(index, total)

        assert self.step.index[0] == index
        assert self.step.index[1] == total
        assert self.step.log is not None


class TestStepBaseInit(StepTestBase):
    def test_missing_optional_keys_are_added(self):
        assert 'depends' in self.step.config.data


class TestStepBaseGetCommand(StepTestBase):
    def test_get_command_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.step.get_command()


class TestCommandLineStepGetCommand(object):
    def setup_method(self, method):
        self.command = '/usr/bin/empathy'
        self.step = CommandLineStep(
            mock.Mock(),
            {'command': self.command},
            'key',
        )

    def test_get_command(self):
        ret = self.step.get_command()
        assert ret == self.command


class TestCommandLineStepValidate(object):
    def setup_method(self, method):
        config = {
            'class': 'piper.step.CommandLineStep',
            'command': 'command'
        }
        self.step = CommandLineStep(mock.Mock(), config, 'key')

    @mock.patch('jsonschema.validate')
    def test_validate_called(self, jv):
        self.step.validate()
        jv.assert_called_once_with(self.step.config.data, self.step.schema)

    def test_validation(self):
        self.step.validate()
