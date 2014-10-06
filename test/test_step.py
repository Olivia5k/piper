from piper.step import Step
from piper.step import CommandLineStep

import mock
import pytest


class StepTest(object):
    def setup_method(self, method):
        self.key = 'test'
        self.schema = {
            'class': 'piper.step.Step',
            'requirements': {
                'reason': 'You can fly, reach for the sky',
                'class': 'edguy.hellfire.Glory',
                'key': 'Rise Of The',
                'equals': 'Morning Glory',
            },
        }
        self.step = Step(self.schema, self.key)


class CommandLineStepTest(object):
    def setup_method(self, method):
        self.key = 'test'
        self.command = '/usr/bin/empathy'
        self.schema = {
            'class': 'piper.step.CommandLineStep',
            'command': self.command,
            'requirements': {
                'reason': 'You can fly, reach for the sky',
                'class': 'edguy.hellfire.Glory',
                'key': 'Rise Of The',
                'equals': 'Morning Glory',
            },
        }
        self.step = CommandLineStep(self.schema, self.key)


class TestStepSchema(StepTest):
    def test_validate(self):
        self.step.validate()

    def test_validate_with_no_requirements(self):
        self.step.config['requirements'] = None
        self.step.validate()


class TestStepSetIndex(StepTest):
    def test_set_index(self):
        index, total = mock.Mock(), mock.Mock()
        self.step.set_index(index, total)

        assert self.step.index[0] == index
        assert self.step.index[1] == total
        assert self.step.log is not None


class TestStepGetCommand(StepTest):
    def test_get_command_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.step.get_command()


class TestCommandLineStepSchema(CommandLineStepTest):
    def test_validate(self):
        self.step.validate()

    def test_validate_with_no_requirements(self):
        self.step.config['requirements'] = None
        self.step.validate()


class TestCommandLineStepGetCommand(CommandLineStepTest):
    def test_get_command(self):
        ret = self.step.get_command()
        assert ret == self.command
