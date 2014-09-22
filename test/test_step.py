from piper.step import StepBase
from piper.step import CommandLineStep

import mock
import pytest


class StepTestBase(object):
    def setup_method(self, method):
        self.step = StepBase(
            mock.Mock(**{'class': 'piper.step.Class'}),
            'key'
        )


class TestStepBaseSetIndex(StepTestBase):
    def test_set_index(self):
        index, total = mock.Mock(), mock.Mock()
        self.step.set_index(index, total)

        assert self.step.index[0] == index
        assert self.step.index[1] == total
        assert self.step.log is not None


class TestStepBaseGetCommand(StepTestBase):
    def test_get_command_raises_notimplementederror(self):
        with pytest.raises(NotImplementedError):
            self.step.get_command()


class TestCommandLineStepGetCommand(object):
    def setup_method(self, method):
        self.command = '/usr/bin/empathy'
        self.step = CommandLineStep(
            {'command': self.command},
            'key',
        )

    def test_get_command(self):
        ret = self.step.get_command()
        assert ret == self.command
