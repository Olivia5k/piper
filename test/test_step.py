from piper.step import StepBase
from piper.step import CommandLineStep

import mock
import pytest


class TestStepBaseValidate(object):
    def setup_method(self, method):
        self.step = StepBase('key', {})

    @mock.patch('jsonschema.validate')
    def test_validate(self, jv):
        self.step.validate()
        jv.assert_called_once_with(self.step.config.data, self.step.schema)


class TestStepBaseSetIndex(object):
    def setup_method(self, method):
        self.step = StepBase('key', {})

    def test_set_index(self):
        index, total = mock.Mock(), mock.Mock()
        self.step.set_index(index, total)

        assert self.step.index[0] == index
        assert self.step.index[1] == total
        assert self.step.log is not None


class TestStepBaseInit(object):
    def test_missing_optional_keys_are_added(self):
        step = StepBase('key', {})
        assert 'depends' in step.config.data


class TestStepBaseGetCommand(object):
    def test_get_command_raises_notimplementederror(self):
        step = StepBase('key', {})
        with pytest.raises(NotImplementedError):
            step.get_command()


class TestCommandLineStepGetCommand(object):
    def setup_method(self, method):
        self.command = '/usr/bin/empathy'
        self.step = CommandLineStep('key', {'command': self.command})

    def test_get_command(self):
        ret = self.step.get_command()
        assert ret == self.command


class TestCommandLineStepValidate(object):
    def setup_method(self, method):
        self.step = CommandLineStep('key', {
            'class': 'piper.step.CommandLineStep',
            'command': 'command'
        })

    @mock.patch('jsonschema.validate')
    def test_validate_called(self, jv):
        self.step.validate()
        jv.assert_called_once_with(self.step.config.data, self.step.schema)

    def test_validation(self):
        # If no exception, is win
        self.step.validate()
