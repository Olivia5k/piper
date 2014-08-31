from piper.step import Step

import mock


class TestStepExecute(object):
    def setup_method(self, method):
        self.command = '/usr/bin/empathy'
        self.step = Step('key', {'command': self.command})

    def test_get_command(self):
        ret = self.step.get_command()
        assert ret == self.command


class TestStepValidate(object):
    def setup_method(self, method):
        self.step = Step('key', {})

    @mock.patch('jsonschema.validate')
    def test_validate(self, jv):
        self.step.validate()
        jv.assert_called_once_with(self.step.config.data, self.step.schema)


class TestStepSetIndex(object):
    def setup_method(self, method):
        self.step = Step('key', {})

    def test_set_index(self):
        index, total = mock.Mock(), mock.Mock()
        self.step.set_index(index, total)

        assert self.step.index[0] == index
        assert self.step.index[1] == total
        assert self.step.log is not None
